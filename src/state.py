import operator
from typing import Annotated, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# --- Detective Output ---
# Used by RepoInvestigator and DocAnalyst to report factual findings
class Evidence(BaseModel):
    goal: str = Field(description="The specific search objective")
    found: bool = Field(description="Whether the artifact exists")
    content: Optional[str] = Field(default=None, description="The extracted snippet or data")
    location: str = Field(description="File path or commit hash")
    rationale: str = Field(description="Confidence rationale for this evidence")
    confidence: float = Field(ge=0.0, le=1.0)

# --- Judge Output ---
# Captured from the Prosecutor, Defense, and Tech Lead
class JudicialOpinion(BaseModel):
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    criterion_id: str = Field(description="The ID of the rubric dimension being judged")
    score: int = Field(ge=1, le=5) 
    argument: str = Field(description="The reasoning behind the score")
    cited_evidence: List[str] = Field(description="References to Evidence objects")

# --- Chief Justice Output ---
# The synthesis of the dialectical conflict for a single rubric dimension
class CriterionResult(BaseModel):
    dimension_id: str
    dimension_name: str
    final_score: int = Field(ge=1, le=5)
    judge_opinions: List[JudicialOpinion]
    dissent_summary: Optional[str] = Field(
        default=None, 
        description="Required when judge score variance > 2"
    )
    remediation: str = Field(description="File-level instructions for improvement") 
# The production-grade final output
class AuditReport(BaseModel):
    repo_url: str
    executive_summary: str
    overall_score: float
    criteria: List[CriterionResult] 
    remediation_plan: str 
# --- Graph State ---
# This is the 'heart' of your LangGraph swarm
class AgentState(TypedDict):
    repo_url: str
    pdf_path: str 
    rubric_dimensions: List[Dict]   

    # The 'operator.ior' reducer merges dictionaries (detective outputs)
    evidences: Annotated[Dict[str, List[Evidence]], operator.ior] 
    
    # The 'operator.add' reducer appends new opinions to the list (judge outputs)
    opinions: Annotated[List[JudicialOpinion], operator.add]
    
    final_report: AuditReport 