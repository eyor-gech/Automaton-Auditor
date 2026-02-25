from langgraph.graph import StateGraph, START, END
from src.state import AgentState, Evidence
from src.nodes.detectives import repo_investigator_node, doc_analyst_node

# 1. Initialize the Graph with the schema
builder = StateGraph(AgentState)

#  WRAPPERS FOR ERROR HANDLING 

def safe_repo_investigator(state: AgentState) -> dict:
    """Error-resilient wrapper for repo analysis."""
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
    """Error-resilient wrapper for document analysis."""
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

# 2. Add Wrapped Nodes
builder.add_node("repo_investigator", safe_repo_investigator)
builder.add_node("doc_analyst", safe_doc_analyst)

# 3. Aggregator Node (Already mostly safe, but let's ensure it handles missing data)
def evidence_aggregator(state: AgentState) -> dict:
    """Forensic Cross-Referencing with safety checks."""
    repo_ev = state.get("evidences", {}).get("repo_investigator", [])
    doc_ev = state.get("evidences", {}).get("doc_analyst", [])
    
    # Check for systemic errors caught by wrappers
    if any("CRITICAL ERROR" in e.rationale for e in repo_ev + doc_ev):
        return {"evidences": {"aggregator": [Evidence(
            goal="System Integrity",
            found=False,
            location="Swarm Infrastructure",
            rationale="Audit halted for specific branch due to I/O failure.",
            confidence=1.0
        )]}}

    # Logic Sync: Claims vs Reality
    pdf_claims_parallel = "Parallel Execution" in str(doc_ev[0].content) if doc_ev else False
    ast_found_parallel = any(e.found for e in repo_ev if "parallel" in e.goal.lower())
    
    conflicts = []
    if pdf_claims_parallel and not ast_found_parallel:
        conflicts.append(Evidence(
            goal="Cross-reference Parallelism",
            found=False,
            location="Logic Sync",
            rationale="HALLUCINATION ALERT: PDF claims parallel execution, but AST analysis found linear wiring.",
            confidence=1.0
        ))
    
    return {"evidences": {"aggregator": conflicts}} if conflicts else {}

builder.add_node("aggregator", evidence_aggregator)

# 4. Wiring: PARALLEL FAN-OUT
builder.add_edge(START, "repo_investigator")
builder.add_edge(START, "doc_analyst")

# 5. FAN-IN: Synchronize
builder.add_edge("repo_investigator", "aggregator")
builder.add_edge("doc_analyst", "aggregator")

builder.add_edge("aggregator", END)

graph = builder.compile()