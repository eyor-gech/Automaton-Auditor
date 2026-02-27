import operator
from typing import Annotated, Dict, List, Literal, Optional,Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# --- INVARIANT DOCUMENTATION ---
# 1. Evidence.confidence: 1.0 for AST/Deterministic facts, 0.7-0.9 for LLM/Heuristic claims.
# 2. State Merging: 'evidences' uses operator.ior (Dict Union) for parallel detective writes.
# 3. Opinion Merging: 'opinions' uses operator.add for the judicial adversarial debate.

class Evidence(BaseModel):
    goal: str = Field(description="Objective (e.g., 'Verify Parallelism')")
    found: bool = Field(description="Fact existence")
    content: Optional[str] = Field(default=None, description="Raw data snippet")
    location: str = Field(description="Source file or chunk ID")
    rationale: str = Field(description="Why this evidence was marked found/not found")
    confidence: float = Field(ge=0.0, le=1.0, description="1.0=Hard Fact, <1.0=Inference")

class JudicialDecision(BaseModel):
    """
    CONSTITUTIONAL REQUIREMENT: 
    The structured format judges must use for their output to prevent hallucinations.
    """
    score: int = Field(ge=1, le=5, description="Score from 1 to 5")
    reasoning: str = Field(description="Detailed forensic justification")
    citations: List[str] = Field(description="Specific evidence items cited from the forensic logs")

class JudicialOpinion(BaseModel):
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    criterion_id: str 
    score: int = Field(ge=1, le=5) 
    argument: str = Field(description="Adversarial reasoning")
    cited_evidence: List[str] = Field(description="IDs of Evidence objects supporting this view")

class CriterionResult(BaseModel):
    dimension_id: str
    dimension_name: str
    final_score: int = Field(ge=1, le=5)
    judge_opinions: List[JudicialOpinion]
    dissent_summary: Optional[str] = Field(default=None, description="Required if score variance σ² > 2")
    remediation: str 

class AuditReport(BaseModel):
    repo_url: str
    executive_summary: str
    overall_score: float
    criteria: List[CriterionResult] 
    remediation_plan: str 

# A simple reducer that just takes the most recent status update
def merge_status(current: str, new: str) -> str:
    return new

class AgentState(TypedDict):
    repo_url: str
    pdf_path: str 
    rubric: Dict[str, str]
    # Reducer: operator.ior handles merging dictionaries from parallel nodes
    evidences: Annotated[Dict[str, List[Any]], operator.ior] 
    # Reducer: operator.add handles appending opinions to a list
    opinions: Annotated[List[Any], operator.add]
    final_report: Optional[Any]
    
    # FIX: Added Reducers to these keys to handle parallel writes
    status: Annotated[str, merge_status] 
    instructor_feedback: Annotated[str, merge_status]
    
    human_approved: bool 
    repo_path: Optional[str]