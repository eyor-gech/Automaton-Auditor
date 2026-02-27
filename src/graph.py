from typing import Literal
from langgraph.graph import StateGraph, START, END
from src.state import AgentState

# 1. Node Imports
from src.nodes.detectives import (
    repo_investigator_node, 
    doc_analyst_node, 
    vision_inspector_node
)
from src.nodes.judges import (
    prosecutor_node, 
    defense_node, 
    tech_lead_node
)
from src.nodes.chief_justice import chief_justice_node

# ---------------------------------
# 2. AGGREGATOR & ROUTER
# ---------------------------------

def evidence_aggregator(state: AgentState) -> dict:
    """
    CONSTITUTIONAL FAN-IN: Synchronizes all detective evidence.
    Ensures judges receive a complete evidentiary record.
    """
    # Verify we have evidence before proceeding to trial
    evidences = state.get("evidences", {})
    if not evidences:
        return {"status": "error_no_evidence"}
        
    return {"status": "evidence_synchronized"}

# ---------------------------------
# 3. GRAPH CONSTRUCTION
# ---------------------------------

builder = StateGraph(AgentState)

# --- Add Detective Nodes ---
builder.add_node("repo_investigator", repo_investigator_node)
builder.add_node("doc_analyst", doc_analyst_node)
builder.add_node("vision_inspector", vision_inspector_node)
builder.add_node("aggregator", evidence_aggregator)

# --- Add Judicial Nodes (Phase 4) ---
builder.add_node("prosecutor", prosecutor_node)
builder.add_node("defense", defense_node)
builder.add_node("tech_lead", tech_lead_node)
builder.add_node("chief_justice", chief_justice_node)

# ---------------------------------
# 4. THE CONSTITUTIONAL WIRING
# ---------------------------------

# LAYER 1: Parallel Fact-Finding (Fan-Out)
builder.add_edge(START, "repo_investigator")
builder.add_edge(START, "doc_analyst")
builder.add_edge(START, "vision_inspector")

# LAYER 2: Synchronization (Fan-In)
builder.add_edge("repo_investigator", "aggregator")
builder.add_edge("doc_analyst", "aggregator")
builder.add_edge("vision_inspector", "aggregator")

# LAYER 3: Adversarial Debate (Fan-Out)
builder.add_edge("aggregator", "prosecutor")
builder.add_edge("aggregator", "defense")
builder.add_edge("aggregator", "tech_lead")

# LAYER 4: Synthesis & Verdict (Fan-In)
builder.add_edge("prosecutor", "chief_justice")
builder.add_edge("defense", "chief_justice")
builder.add_edge("tech_lead", "chief_justice")

# Final Exit
builder.add_edge("chief_justice", END)

# Compile the Graph
graph = builder.compile()