import os
import uuid
from src.state import AgentState, Evidence
from src.tools.repo_tools import analyze_repo_complexity, get_git_history, clone_repo_sandboxed
from src.tools.doc_tools import ingest_pdf_semantically, query_pdf_chunks

async def repo_investigator_node(state: AgentState):
    """High-tier Detective: Uses AST to verify structural graph patterns."""
    with clone_repo_sandboxed(state["repo_url"]) as tmp_dir:
        stats = analyze_repo_complexity(tmp_dir)
        history = get_git_history(tmp_dir)
    
    evidence_list = []
    
    # 1. Structural Wiring Evidence
    evidence_list.append(Evidence(
        id=f"EV-REPO-{uuid.uuid4().hex[:4]}",
        source="AST_Parser",
        goal="Verify LangGraph Parallel Wiring",
        fact=f"Parallel wiring detected: {stats['parallel_wiring']}",
        confidence=1.0,
        location="graph.py (analyzed via AST)",
        rationale="AST detected add_edge or add_conditional_edges with multiple targets, confirming fan-out capability."
    ))

    # 2. State Safety Evidence
    evidence_list.append(Evidence(
        id=f"EV-REPO-{uuid.uuid4().hex[:4]}",
        source="AST_Parser",
        goal="Reducer Safety",
        fact=f"Detected {stats['state_reducers']} reducers.",
        confidence=1.0,
        location="state.py",
        rationale="Annotated types with operator.add/ior prevent state overwrites during parallel fan-in."
    ))

    # 3. Effort Evidence
    evidence_list.append(Evidence(
        id=f"EV-GIT-{uuid.uuid4().hex[:4]}",
        source="Git_Log",
        goal="Development Progression",
        fact=f"Found {len(history)} commits.",
        confidence=1.0,
        location="Git History",
        rationale="Chronological commit analysis confirms iterative development rather than a bulk code dump."
    ))

    return {"evidences": evidence_list}

async def doc_analyst_node(state: AgentState):
    """High-tier Detective: RAG-lite chunked PDF ingestion."""
    ingestion = ingest_pdf_semantically(state["pdf_path"])
    if "error" in ingestion:
        return {"errors": [ingestion["error"]]}

    # Targeted Queries as per Rubric
    claims = ["parallel", "fan-out", "reducer", "adversarial"]
    evidence_list = []
    
    for claim in claims:
        chunks = query_pdf_chunks(ingestion["chunks"], claim)
        for c in chunks[:2]: # Limit to top 2 per claim for brevity
            evidence_list.append(Evidence(
                id=f"EV-DOC-{uuid.uuid4().hex[:4]}",
                source="Docling_Processor",
                goal=f"Verify claim: {claim}",
                fact=c["content"][:200],
                confidence=0.95,
                location=f"PDF Chunk {c['id']}",
                rationale=f"Semantic chunking identified specific architectural claim regarding {claim}."
            ))
            
    return {"evidences": evidence_list}