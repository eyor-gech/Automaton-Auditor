from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes.detectives import repo_investigator_node, doc_analyst_node
from src.state import AgentState, Evidence

# 1. Initialize the Graph with the schema
builder = StateGraph(AgentState)

# 2. Add Detective Nodes
builder.add_node("repo_investigator", repo_investigator_node)
builder.add_node("doc_analyst", doc_analyst_node)

# 3. Aggregator Node
def evidence_aggregator(state: AgentState) -> dict:
    """
    Forensic Cross-Referencing: Compares PDF claims vs Repo facts.
    This creates 'Conflict Evidence' for the Judges to review.
    """
    repo_ev = state["evidences"].get("repo_investigator", [])
    doc_ev = state["evidences"].get("doc_analyst", [])
    
    # Check: Did the PDF claim 'Parallel' but AST found 'Linear'?
    pdf_claims_parallel = "Parallel Execution" in str(doc_ev[0].content) if doc_ev else False
    ast_found_parallel = any(e.found for e in repo_ev if "parallel" in e.goal.lower())
    
    conflicts = []
    if pdf_claims_parallel and not ast_found_parallel:
        conflicts.append(Evidence(
            goal="Cross-reference Parallelism",
            found=False,
            location="Logic Sync",
            rationale="HALLUCINATION ALERT: PDF claims parallel execution, but AST analysis of src/graph.py found linear wiring.",
            confidence=1.0
        ))
    
    # If conflicts exist, we add them to the evidence pool
    if conflicts:
        return {"evidences": {"aggregator": conflicts}}
    
    return {} # No changes needed if no conflicts

builder.add_node("aggregator", evidence_aggregator)

# 4. Phase 3 Wiring: PARALLEL FAN-OUT
# Both detectives start at the same time
builder.add_edge(START, "repo_investigator")
builder.add_edge(START, "doc_analyst")

# 5. FAN-IN: Synchronize before moving to Judges
builder.add_edge("repo_investigator", "aggregator")
builder.add_edge("doc_analyst", "aggregator")

builder.add_edge("aggregator", END)

graph = builder.compile()