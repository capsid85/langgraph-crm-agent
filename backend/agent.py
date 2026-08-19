import os
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchResults
from hubspot import HubSpot
from hubspot.crm.companies import SimplePublicObjectInput, ApiException
from models import AgentState, EnrichmentData
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize LLM (Ollama)
llm = ChatOllama(model="llama3", temperature=0)

# Initialize Search Tool
search_tool = DuckDuckGoSearchResults(num_results=5)

# Initialize HubSpot Client
hubspot_api_key = os.getenv("HUBSPOT_ACCESS_TOKEN")
hubspot_client = HubSpot(access_token=hubspot_api_key) if hubspot_api_key else None

def search_web(state: AgentState) -> Dict[str, Any]:
    print(f"[Agent] Searching web for: {state.company_name}")
    try:
        query = f"{state.company_name} company industry size technology stack news"
        results = search_tool.invoke(query)
        return {"search_results": results, "status": "search_completed"}
    except Exception as e:
        return {"errors": state.errors + [f"Web search failed: {str(e)}"], "status": "search_failed"}

def extract_info(state: AgentState) -> Dict[str, Any]:
    print(f"[Agent] Extracting info for: {state.company_name}")
    if not state.search_results:
        return {"errors": state.errors + ["No search results to extract from."], "status": "extraction_failed"}
    
    try:
        prompt = f"""
        Extract structured enrichment data for the company '{state.company_name}' based on the following search results:
        
        {state.search_results}
        
        If you cannot find specific information, leave it empty or null.
        """
        # Use structured output
        structured_llm = llm.with_structured_output(EnrichmentData)
        extracted_data = structured_llm.invoke(prompt)
        return {"enrichment_data": extracted_data, "status": "extraction_completed"}
    except Exception as e:
        return {"errors": state.errors + [f"Extraction failed: {str(e)}"], "status": "extraction_failed"}

def validate_info(state: AgentState) -> Dict[str, Any]:
    print(f"[Agent] Validating info for: {state.company_name}")
    data = state.enrichment_data
    if not data or (not data.industry and not data.size and not data.domain):
        return {"errors": state.errors + ["Extracted data is too sparse to be useful."], "status": "validation_failed"}
    return {"status": "validation_completed"}

def resolve_crm_record(state: AgentState) -> Dict[str, Any]:
    print(f"[Agent] Resolving CRM record for: {state.company_name}")
    if not hubspot_client:
        print("[Agent] HubSpot client not configured (mock mode)")
        return {"status": "crm_resolved", "hubspot_company_id": "mock_id_123"}
        
    try:
        # Search HubSpot for existing company by name or domain
        search_request = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "name",
                            "operator": "EQ",
                            "value": state.company_name
                        }
                    ]
                }
            ],
            "properties": ["name", "domain"]
        }
        if state.enrichment_data and state.enrichment_data.domain:
            search_request["filterGroups"].append(
                {
                    "filters": [
                        {
                            "propertyName": "domain",
                            "operator": "EQ",
                            "value": state.enrichment_data.domain
                        }
                    ]
                }
            )
            
        public_object_search_request = search_request
        api_response = hubspot_client.crm.companies.search_api.do_search(public_object_search_request=public_object_search_request)
        
        if api_response.results:
            company_id = api_response.results[0].id
            print(f"[Agent] Found existing HubSpot company: {company_id}")
            return {"hubspot_company_id": company_id, "status": "crm_resolved"}
        else:
            print("[Agent] No existing HubSpot company found.")
            return {"hubspot_company_id": None, "status": "crm_resolved"}
            
    except ApiException as e:
        return {"errors": state.errors + [f"HubSpot search failed: {e.reason}"], "status": "crm_resolution_failed"}
    except Exception as e:
        return {"errors": state.errors + [f"HubSpot search failed: {str(e)}"], "status": "crm_resolution_failed"}

def write_to_crm(state: AgentState) -> Dict[str, Any]:
    print(f"[Agent] Writing to CRM for: {state.company_name}")
    if not hubspot_client:
        print("[Agent] HubSpot client not configured. Skipping write (mock mode).")
        return {"status": "completed"}
        
    data = state.enrichment_data
    properties = {
        "name": state.company_name,
        "industry": data.industry if data and data.industry else "",
        "numberofemployees": data.size if data and data.size else "",
        "domain": data.domain if data and data.domain else "",
        "description": f"Tech Stack: {', '.join(data.tech_stack) if data and data.tech_stack else 'N/A'}\nRecent News: {data.recent_news if data and data.recent_news else 'N/A'}"
    }
    
    try:
        if state.hubspot_company_id:
            # Update existing
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            hubspot_client.crm.companies.basic_api.update(
                company_id=state.hubspot_company_id,
                simple_public_object_input=simple_public_object_input
            )
            print(f"[Agent] Updated HubSpot company: {state.hubspot_company_id}")
        else:
            # Create new
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            api_response = hubspot_client.crm.companies.basic_api.create(
                simple_public_object_input=simple_public_object_input
            )
            print(f"[Agent] Created new HubSpot company: {api_response.id}")
            return {"hubspot_company_id": api_response.id, "status": "completed"}
            
        return {"status": "completed"}
    except ApiException as e:
        return {"errors": state.errors + [f"HubSpot write failed: {e.reason}"], "status": "write_failed"}
    except Exception as e:
         return {"errors": state.errors + [f"HubSpot write failed: {str(e)}"], "status": "write_failed"}

# Define routing logic for retries / failures
def should_continue_after_search(state: AgentState):
    if state.status == "search_failed":
        return END
    return "extract_info"

def should_continue_after_extract(state: AgentState):
    if state.status == "extraction_failed":
        return END
    return "validate_info"
    
def should_continue_after_validate(state: AgentState):
    if state.status == "validation_failed":
        return END
    return "resolve_crm_record"

def should_continue_after_resolve(state: AgentState):
    if state.status == "crm_resolution_failed":
        return END
    return "write_to_crm"

# Build Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("search_web", search_web)
workflow.add_node("extract_info", extract_info)
workflow.add_node("validate_info", validate_info)
workflow.add_node("resolve_crm_record", resolve_crm_record)
workflow.add_node("write_to_crm", write_to_crm)

# Add Edges
workflow.set_entry_point("search_web")
workflow.add_conditional_edges("search_web", should_continue_after_search, {"extract_info": "extract_info", END: END})
workflow.add_conditional_edges("extract_info", should_continue_after_extract, {"validate_info": "validate_info", END: END})
workflow.add_conditional_edges("validate_info", should_continue_after_validate, {"resolve_crm_record": "resolve_crm_record", END: END})
workflow.add_conditional_edges("resolve_crm_record", should_continue_after_resolve, {"write_to_crm": "write_to_crm", END: END})
workflow.add_edge("write_to_crm", END)

# Compile Agent
agent = workflow.compile()
