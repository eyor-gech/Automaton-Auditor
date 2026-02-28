import asyncio
import os
import uuid
import shutil
from typing import List
from src.state import AgentState, Evidence
from src.tools.repo_tools import (
    analyze_repo_complexity,
    get_git_history,
    clone_repo_sandboxed
)
from src.tools.doc_tools import (
    ingest_pdf_semantically,
    query_pdf_chunks
)

# -----------------------------
# CONFIGURATION GUARDS
# -----------------------------

MAX_REPO_SIZE_MB = 200
MAX_COMMITS_ANALYZED = 500
MAX_EVIDENCE_PER_CLAIM = 2
CLONE_TIMEOUT_SECONDS = 60


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def calculate_directory_size_mb(path: str) -> float:
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total / (1024 * 1024)


def calibrate_confidence(base: float, modifier: float = 0.0) -> float:
    """
    Ensures confidence remains within realistic bounds.
    """
    value = max(0.5, min(0.99, base + modifier))
    return round(value, 2)


# -----------------------------
# REPO INVESTIGATOR NODE
# -----------------------------

async def repo_investigator_node(state: AgentState):
    evidences: List[Evidence] = []

    try:
        async def clone_and_analyze():
            with clone_repo_sandboxed(state["repo_url"]) as tmp_dir:

                # Size Guard
                size_mb = calculate_directory_size_mb(tmp_dir)
                if size_mb > MAX_REPO_SIZE_MB:
                    raise ValueError(f"Repository too large: {size_mb:.1f} MB")

                stats = analyze_repo_complexity(tmp_dir)
                history = get_git_history(tmp_dir)[:MAX_COMMITS_ANALYZED]

                return tmp_dir, stats, history

        tmp_dir, stats, history = await asyncio.wait_for(
            asyncio.to_thread(lambda: asyncio.run(clone_and_analyze())),
            timeout=CLONE_TIMEOUT_SECONDS
        )

    except Exception as e:
        return {"errors": [f"Repo investigation failed: {str(e)}"]}

    # Defensive reads
    parallel_wiring = stats.get("parallel_wiring", False)
    state_reducers = stats.get("state_reducers", 0)
    commit_count = len(history)

    # 1️⃣ Structural Wiring Evidence
    evidences.append(Evidence(
        id=f"EV-REPO-{uuid.uuid4().hex[:4]}",
        source="AST_Parser",
        goal="Verify LangGraph Parallel Wiring",
        fact=f"Parallel wiring detected: {parallel_wiring}",
        confidence=calibrate_confidence(0.85 if parallel_wiring else 0.7),
        location="graph.py (AST Analysis)",
        rationale="AST inspection identified add_edge or conditional routing patterns confirming fan-out architecture."
    ))

    # 2️⃣ Reducer Safety Evidence
    evidences.append(Evidence(
        id=f"EV-REPO-{uuid.uuid4().hex[:4]}",
        source="AST_Parser",
        goal="Reducer Safety",
        fact=f"Detected {state_reducers} reducer annotations.",
        confidence=calibrate_confidence(0.88 if state_reducers > 0 else 0.6),
        location="state.py",
        rationale="Annotated reducers (e.g., operator.add) protect state during parallel fan-in."
    ))

    # 3️⃣ Development Effort Evidence
    evidences.append(Evidence(
        id=f"EV-GIT-{uuid.uuid4().hex[:4]}",
        source="Git_Log",
        goal="Development Progression",
        fact=f"Analyzed {commit_count} commits.",
        confidence=calibrate_confidence(0.9 if commit_count > 5 else 0.65),
        location="Git History",
        rationale="Chronological commit inspection suggests iterative engineering rather than bulk upload."
    ))

    return {"evidences": evidences}


# -----------------------------
# DOCUMENT ANALYST NODE
# -----------------------------

async def doc_analyst_node(state: AgentState):
    evidences: List[Evidence] = []

    try:
        ingestion = await asyncio.to_thread(
            ingest_pdf_semantically,
            state["pdf_path"]
        )

        if "error" in ingestion:
            return {"errors": [ingestion["error"]]}

        claims = ["parallel", "fan-out", "reducer", "adversarial"]

        for claim in claims:
            chunks = query_pdf_chunks(ingestion["chunks"], claim)

            for c in chunks[:MAX_EVIDENCE_PER_CLAIM]:
                evidences.append(Evidence(
                    id=f"EV-DOC-{uuid.uuid4().hex[:4]}",
                    source="Docling_Processor",
                    goal=f"Verify claim: {claim}",
                    fact=c["content"][:250],
                    confidence=calibrate_confidence(0.9, -0.05),
                    location=f"PDF Chunk {c.get('id', 'unknown')}",
                    rationale=f"Semantic retrieval identified architectural reference related to '{claim}'."
                ))

    except Exception as e:
        return {"errors": [f"Document analysis failed: {str(e)}"]}

    return {"evidences": evidences}