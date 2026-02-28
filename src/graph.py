# -----------------------------
# GRAPH CONSTRUCTION (Refined)
# -----------------------------
builder = StateGraph(AgentState)

# 1️⃣ Add Nodes
nodes = {
    "detect_repo": repo_investigator_node,
    "detect_doc": doc_analyst_node,
    "aggregator": aggregator_node,
    "judges_router": judges_router,
    "prosecutor": prosecutor_node,
    "defense": defense_node,
    "tech_lead": tech_lead_node,
    "chief": chief_justice_node
}
for name, fn in nodes.items():
    builder.add_node(name, fn)

# 2️⃣ START → Detectives (Parallel Fan-Out)
builder.add_edge(START, ["detect_repo", "detect_doc"])

# 3️⃣ Detectives → Aggregator (Fan-In)
builder.add_edge("detect_repo", "aggregator")
builder.add_edge("detect_doc", "aggregator")

# 4️⃣ Aggregator → Conditional Routing (Evidence Check)
builder.add_conditional_edges(
    "aggregator",
    evidence_guard,
    {"ok": "judges_router", "fail": END}
)

# 5️⃣ Judges Router → Judges (Parallel Fan-Out)
builder.add_edge("judges_router", ["prosecutor", "defense", "tech_lead"])

# 6️⃣ Judges → Chief Justice (Fan-In)
builder.add_edge("prosecutor", "chief")
builder.add_edge("defense", "chief")
builder.add_edge("tech_lead", "chief")

# 7️⃣ Chief → END
builder.add_edge("chief", END)

# 8️⃣ Compile Graph
graph = builder.compile()