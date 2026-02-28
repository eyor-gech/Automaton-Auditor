# src/graph.py
from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes.detectives import repo_investigator_node, doc_analyst_node
from src.nodes.aggregator import aggregator_node
from src.nodes.judges import prosecutor_node, defense_node, tech_lead_node
from src.nodes.chief_justice import chief_justice_node

# -----------------------------
# ROUTER & GUARD FUNCTIONS
# -----------------------------
def evidence_guard(state: AgentState):
    """Determines if the audit should continue based on collected evidence.
    Prevents AttributeError when brief is a Pydantic object."""
    brief = state.get("aggregated_brief")
    """
    if not brief or not brief.get("evidences"):
        return "fail"
    return "ok"
    """
    if brief is None:
        print("🚨 CRITICAL: No brief found in state.")
        return "end"

    # Safely extract evidences regardless of object type
    if isinstance(brief, dict):
        evidences = brief.get("evidences", [])
    else:
        # It's a Pydantic model (AggregatedBrief)
        evidences = getattr(brief, "evidences", [])

    if not evidences:
        print("🚨 NO EVIDENCE FOUND: Terminating to prevent Judge hallucinations.")
        return "end"

    print(f"⚖️ Guard passed: {len(evidences)} evidence items ready for trial.")
    return "continue"
    
def judges_router(state: AgentState):
    """Pass-through router for LangGraph conditional edges."""
    return state

# -----------------------------
# GRAPH CONSTRUCTION
# -----------------------------
builder = StateGraph(AgentState)

# 1️⃣ Add Nodes
builder.add_node("detect_repo", repo_investigator_node)
builder.add_node("detect_doc", doc_analyst_node)
builder.add_node("detectives_sync", lambda s: s)  # fan-in synchronization
builder.add_node("aggregator", aggregator_node)
builder.add_node("judges_router", judges_router)
builder.add_node("prosecutor", prosecutor_node)
builder.add_node("defense", defense_node)
builder.add_node("tech_lead", tech_lead_node)
builder.add_node("chief", chief_justice_node)

# 2️⃣ START → Detectives (Parallel Fan-Out)
builder.add_edge(START, "detect_repo")
builder.add_edge(START, "detect_doc")

# 3️⃣ Detectives → Sync Node (Fan-In)
builder.add_edge("detect_repo", "detectives_sync")
builder.add_edge("detect_doc", "detectives_sync")

# 4️⃣ Sync → Aggregator
builder.add_edge("detectives_sync", "aggregator")

# 5️⃣ Aggregator → Conditional Routing
builder.add_conditional_edges(
    "aggregator",
    evidence_guard,
    {
        "ok": "judges_router",
        "fail": END
    }
)

# 6️⃣ Router → Judges (Parallel Fan-Out)
builder.add_edge("judges_router", "prosecutor")
builder.add_edge("judges_router", "defense")
builder.add_edge("judges_router", "tech_lead")

# 7️⃣ Judges → Chief (Fan-In)
builder.add_edge("prosecutor", "chief")
builder.add_edge("defense", "chief")
builder.add_edge("tech_lead", "chief")

# 8️⃣ Chief → END
builder.add_edge("chief", END)

# -----------------------------
# COMPILE GRAPH
# -----------------------------
graph = builder.compile()