from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes.detectives import repo_investigator_node, doc_analyst_node
from src.nodes.aggregator import aggregator_node
from src.nodes.judges import prosecutor_node, defense_node, tech_lead_node
from src.nodes.chief_justice import chief_justice_node


def evidence_guard(state: AgentState):
    """
    Deterministic routing logic.
    If no valid evidence exists, terminate early.
    """
    brief = state.get("aggregated_brief")

    if not brief:
        return "fail"

    evidences = brief.get("evidences", [])
    if not evidences:
        return "fail"

    return "ok"


def judges_router(state: AgentState):
    """
    Pass-through router node.
    Required because LangGraph conditional edges
    cannot return multiple destination nodes.
    """
    return state


# --------------------------------------------------
# GRAPH CONSTRUCTION
# --------------------------------------------------

builder = StateGraph(AgentState)

# 1️⃣ Add Nodes
builder.add_node("detect_repo", repo_investigator_node)
builder.add_node("detect_doc", doc_analyst_node)
builder.add_node("aggregator", aggregator_node)
builder.add_node("judges_router", judges_router)
builder.add_node("prosecutor", prosecutor_node)
builder.add_node("defense", defense_node)
builder.add_node("tech_lead", tech_lead_node)
builder.add_node("chief", chief_justice_node)

# 2️⃣ START → Detectives (Parallel Fan-Out)
builder.add_edge(START, "detect_repo")
builder.add_edge(START, "detect_doc")

# 3️⃣ Detectives → Aggregator (Fan-In)
builder.add_edge("detect_repo", "aggregator")
builder.add_edge("detect_doc", "aggregator")

# 4️⃣ Aggregator → Conditional Routing
builder.add_conditional_edges(
    "aggregator",
    evidence_guard,
    {
        "ok": "judges_router",   # must be single node
        "fail": END
    }
)

# 5️⃣ Router → Judges (Parallel Fan-Out)
builder.add_edge("judges_router", "prosecutor")
builder.add_edge("judges_router", "defense")
builder.add_edge("judges_router", "tech_lead")

# 6️⃣ Judges → Chief (Fan-In)
builder.add_edge("prosecutor", "chief")
builder.add_edge("defense", "chief")
builder.add_edge("tech_lead", "chief")

# 7️⃣ Chief → END
builder.add_edge("chief", END)

# --------------------------------------------------
# COMPILE
# --------------------------------------------------

graph = builder.compile()