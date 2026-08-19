from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models import EnrichmentRequest, EnrichmentResponse
from agent import agent

app = FastAPI(title="HubSpot CRM Enrichment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/enrich", response_model=EnrichmentResponse)
async def enrich_company(request: EnrichmentRequest):
    initial_state = {
        "company_name": request.company_name,
        "errors": []
    }
    
    try:
        # Run the agent
        final_state = agent.invoke(initial_state)
        
        return EnrichmentResponse(
            status=final_state.get("status", "unknown"),
            company_name=final_state.get("company_name"),
            hubspot_company_id=final_state.get("hubspot_company_id"),
            data=final_state.get("enrichment_data"),
            errors=final_state.get("errors", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
