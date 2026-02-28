import operator
from typing import Annotated, Dict, List, Literal, Optional, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class Evidence(BaseModel):
    id: str
    source: str
    fact: str
    confidence: float = Field(ge=0, le=1)
    location: Optional[str] = None
    rationale: Optional[str] = None
    goal: str  # Added to match rubric requirements

class JudicialOpinion(BaseModel):
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    criterion_id: str
    score: int = Field(ge=1, le=5)
    argument: str
    cited_evidence: List[str]

class AggregatedBrief(BaseModel):
    evidences: List[Evidence]
    hallucination_flags: List[str] # or List[Evidence]
    summary: str

class CriterionResult(BaseModel):
    dimension_id: str
    dimension_name: str
    final_score: int = Field(ge=1, le=5)
    judge_opinions: List[JudicialOpinion]
    dissent_summary: Optional[str] = None
    remediation: str

class AuditReport(BaseModel):
    repo_url: str
    executive_summary: str
    overall_score: float
    criteria: List[CriterionResult]
    remediation_plan: str

class AgentState(TypedDict):
    repo_url: str
    pdf_path: str
    rubric_dimensions: List[Dict]
    # Using operator.add for list-based accumulation in parallel nodes
    evidences: Annotated[List, operator.add] 
    opinions: Annotated[List, operator.add]
    aggregated_brief: Optional[dict]
    final_report: Optional[dict]
    errors: Annotated[List[str], operator.add]