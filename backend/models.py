from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class EnrichmentData(BaseModel):
    industry: Optional[str] = Field(description="The primary industry of the company")
    size: Optional[str] = Field(description="Estimated company size (e.g., '1-10', '11-50', '51-200', '201-500', '501-1000', '1000+')")
    tech_stack: Optional[List[str]] = Field(description="List of technologies, frameworks, and tools the company uses")
    recent_news: Optional[str] = Field(description="Summary of recent news or press releases regarding the company")
    domain: Optional[str] = Field(description="The primary website domain of the company")

class AgentState(BaseModel):
    company_name: str
    search_results: Optional[str] = None
    enrichment_data: Optional[EnrichmentData] = None
    hubspot_company_id: Optional[str] = None
    status: str = "started"
    errors: List[str] = []

class EnrichmentRequest(BaseModel):
    company_name: str

class EnrichmentResponse(BaseModel):
    status: str
    company_name: str
    hubspot_company_id: Optional[str] = None
    data: Optional[EnrichmentData] = None
    errors: List[str] = []
