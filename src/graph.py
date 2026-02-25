from langgraph.graph import StateGraph, START, END
from src.state import AgentState, Evidence
from src.nodes.detectives import (
    repo_investigator_node,
    doc_analyst_node,
    vision_inspector_node,
)

builder = StateGraph(AgentState)

# ---------------------------------
# SAFE WRAPPERS (UNCHANGED CORE)
# ---------------------------------

def safe_wrapper(node_fn, label):
    def wrapped(state: AgentState) -> dict:
        try:
            return node_fn(state)
        except Exception as e:
            error_ev = Evidence(
                goal=f"{label} Failure",
                found=False,
                location=f"{label}/System",
                rationale=f"CRITICAL ERROR: {str(e)}",
                confidence=1.0
            )
            return {
                "evidences": {label: [error_ev]},
                "status": "error"
            }
    return wrapped


builder.add_node("repo_investigator", safe_wrapper(repo_investigator_node, "repo"))
builder.add_node("doc_analyst", safe_wrapper(doc_analyst_node, "doc"))
builder.add_node("vision_inspector", safe_wrapper(vision_inspector_node, "vision"))


# ---------------------------------
# AGGREGATOR (FAILURE AWARE)
# ---------------------------------

def evidence_aggregator(state: AgentState) -> dict:
    evidences = state.get("evidences", {})
    status = state.get("status")

    conflicts = []

    if status == "error":
        conflicts.append(Evidence(
            goal="Pipeline Integrity",
            found=False,
            location="Graph",
            rationale="One or more detectives failed.",
            confidence=1.0
        ))

    return {"evidences": {"aggregator": conflicts}} if conflicts else {}


builder.add_node("aggregator", evidence_aggregator)


# ---------------------------------
# CONDITIONAL EDGES
# ---------------------------------

def route_on_status(state: AgentState):
    if state.get("status") == "error":
        return "aggregator"
    return "aggregator"


builder.add_conditional_edges(
    "repo_investigator",
    route_on_status
)

builder.add_conditional_edges(
    "doc_analyst",
    route_on_status
)

builder.add_conditional_edges(
    "vision_inspector",
    route_on_status
)


# ---------------------------------
# PARALLEL FAN-OUT
# ---------------------------------

builder.add_edge(START, "repo_investigator")
builder.add_edge(START, "doc_analyst")
builder.add_edge(START, "vision_inspector")

# FAN-IN
builder.add_edge("repo_investigator", "aggregator")
builder.add_edge("doc_analyst", "aggregator")
builder.add_edge("vision_inspector", "aggregator")

builder.add_edge("aggregator", END)


# ---------------------------------
# JUDICIAL EXTENSION SKETCH
# ---------------------------------
"""
Future Judicial Layer:

aggregator → judicial_reasoner_1
aggregator → judicial_reasoner_2
aggregator → judicial_reasoner_3

Then:

judicial_reasoner_* → final_verdict_node → END

This enables:
- Multi-judge reasoning
- Majority voting
- Confidence aggregation
- Legal-grade explainability
"""

graph = builder.compile()