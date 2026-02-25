from langgraph.graph import StateGraph, START, END
from src.state import AgentState, Evidence
from src.nodes.detectives import repo_investigator_node, doc_analyst_node, vision_inspector_node

# 1. Initialize the Graph
builder = StateGraph(AgentState)

# --- WRAPPERS FOR ERROR HANDLING ---

def safe_repo_investigator(state: AgentState) -> dict:
    try:
        return repo_investigator_node(state)
    except Exception as e:
        error_ev = Evidence(
            goal="Repo Investigation",
            found=False,
            location="Git/System",
            rationale=f"CRITICAL ERROR: {str(e)}",
            confidence=1.0
        )
        return {"evidences": {"repo_investigator": [error_ev]}}

def safe_doc_analyst(state: AgentState) -> dict:
    try:
        return doc_analyst_node(state)
    except Exception as e:
        error_ev = Evidence(
            goal="Document Analysis",
            found=False,
            location="PDF/System",
            rationale=f"CRITICAL ERROR: {str(e)}",
            confidence=1.0
        )
        return {"evidences": {"doc_analyst": [error_ev]}}

def safe_vision_inspector(state: AgentState) -> dict:
    try:
        return vision_inspector_node(state)
    except Exception as e:
        error_ev = Evidence(
            goal="Vision Analysis",
            found=False,
            location="Image/System",
            rationale=f"CRITICAL ERROR: {str(e)}",
            confidence=1.0
        )
        return {"evidences": {"vision_inspector": [error_ev]}}

# 2. Add All Detective Nodes
builder.add_node("repo_investigator", safe_repo_investigator)
builder.add_node("doc_analyst", safe_doc_analyst)
builder.add_node("vision_inspector", safe_vision_inspector)

# 3. Aggregator Node
def evidence_aggregator(state: AgentState) -> dict:
    """Forensic Cross-Referencing: Repo vs Doc vs Vision."""
    repo_ev = state.get("evidences", {}).get("repo_investigator", [])
    doc_ev = state.get("evidences", {}).get("doc_analyst", [])
    vision_ev = state.get("evidences", {}).get("vision_inspector", [])
    
    # Logic Sync: Check for conflicts
    pdf_claims_parallel = "Parallel Execution" in str(doc_ev[0].content) if doc_ev else False
    ast_found_parallel = any(e.found for e in repo_ev if "parallel" in e.goal.lower())
    
    conflicts = []
    # Conflict 1: Text vs Code
    if pdf_claims_parallel and not ast_found_parallel:
        conflicts.append(Evidence(
            goal="Cross-reference Parallelism",
            found=False,
            location="Logic Sync",
            rationale="HALLUCINATION ALERT: PDF text claims parallel execution, but AST found linear wiring.",
            confidence=1.0
        ))
    
    # Conflict 2: Vision vs Code (If images exist but code is linear)
    has_diagrams = any(e.found for e in vision_ev)
    if has_diagrams and not ast_found_parallel:
        conflicts.append(Evidence(
            goal="Visual vs Structural Sync",
            found=False,
            location="Architecture Sync",
            rationale="DISCREPANCY: Architecture diagrams exist, but code does not implement the parallel patterns shown.",
            confidence=0.8
        ))
    
    return {"evidences": {"aggregator": conflicts}} if conflicts else {}

builder.add_node("aggregator", evidence_aggregator)

# 4. TRIPLE FAN-OUT (The Multi-Modal Split)
builder.add_edge(START, "repo_investigator")
builder.add_edge(START, "doc_analyst")
builder.add_edge(START, "vision_inspector")

# 5. FAN-IN (The Forensic Sync)
builder.add_edge("repo_investigator", "aggregator")
builder.add_edge("doc_analyst", "aggregator")
builder.add_edge("vision_inspector", "aggregator")

builder.add_edge("aggregator", END)

graph = builder.compile()