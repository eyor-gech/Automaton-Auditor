from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes.detectives import repo_investigator_node, doc_analyst_node
from src.nodes.aggregator import aggregator_node
from src.nodes.judges import prosecutor_node, defense_node, tech_lead_node
from src.nodes.chief_justice import chief_justice_node

def evidence_guard(state: AgentState):
    """
    Deterministic Router: Ensures we don't waste LLM tokens if 
    detectives fail to find usable evidence.
    """
    brief = state.get("aggregated_brief")
    if not brief or not getattr(brief, 'evidences', None) or len(brief.evidences) == 0:
        return "fail"
    return "ok"

builder = StateGraph(AgentState)

# --- 1. Detective Layer (Parallel Fan-Out) ---
builder.add_node("detect_repo", repo_investigator_node)
builder.add_node("detect_doc", doc_analyst_node)

# --- 2. Aggregator (Fan-In / Sync Point) ---
builder.add_node("aggregator", aggregator_node)

# --- 3. Judicial Layer (Parallel Fan-Out) ---
builder.add_node("prosecutor", prosecutor_node)
builder.add_node("defense", defense_node)
builder.add_node("tech_lead", tech_lead_node)

# --- 4. Chief Justice (Synthesis Point) ---
builder.add_node("chief", chief_justice_node)

# --- Defined Flow ---

# START -> Parallel Detectives
builder.add_edge(START, "detect_repo")
builder.add_edge(START, "detect_doc")

# Parallel Detectives -> Aggregator (Sync)
builder.add_edge("detect_repo", "aggregator")
builder.add_edge("detect_doc", "aggregator")

# Aggregator -> Conditional Guard -> Parallel Judges
builder.add_conditional_edges(
    "aggregator",
    evidence_guard,
    {
        "ok": ["prosecutor", "defense", "tech_lead"],
        "fail": END
    }
)

# Parallel Judges -> Chief Justice (Final Sync)
builder.add_edge("prosecutor", "chief")
builder.add_edge("defense", "chief")
builder.add_edge("tech_lead", "chief")

# Chief Justice -> END
builder.add_edge("chief", END)

graph = builder.compile()