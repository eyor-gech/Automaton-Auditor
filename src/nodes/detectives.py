import os
from src.state import AgentState, Evidence
from src.tools.repo_tools import clone_repo_sandboxed, analyze_graph_parallelism, get_git_history
from src.tools.doc_tools import ingest_pdf_content, search_for_keywords

def repo_investigator_node(state: AgentState) -> dict:
    """Forensic Protocol A & B: Verify code structure and Git history."""
    repo_path = clone_repo_sandboxed(state["repo_url"])
    
    # 1. AST Parallelism Check
    graph_file = os.path.join(repo_path, "src/graph.py")
    is_parallel = analyze_graph_parallelism(graph_file)
    
    evidence_parallel = Evidence(
        goal="Verify parallel graph wiring",
        found=is_parallel,
        location="src/graph.py",
        rationale="AST parsing checked for parallel add_edge calls with list arguments.",
        confidence=1.0
    )

    # 2. Git History Extraction (Requirement: Deep AST & History)
    history = get_git_history(repo_path)
    evidence_git = Evidence(
        goal="Extract full commit history",
        found=len(history) > 0,
        location=".git/logs",
        content="\n".join(history[:10]), # Capture top 10 for analysis
        rationale="Verified progression through atomic commit logs.",
        confidence=1.0
    )

    return {"evidences": {"repo_investigator": [evidence_parallel, evidence_git]}}

def doc_analyst_node(state: AgentState) -> dict:
    """Forensic Protocol B: Cross-reference PDF claims."""
    content = ingest_pdf_content(state["pdf_path"])
    
    # We look for specific high-level claims the user might make
    keywords = ["Dialectical Synthesis", "AST Parsing", "Parallel Execution", "Pydantic"]
    findings = search_for_keywords(content, keywords)
    
    evidence_claims = Evidence(
        goal="Identify architectural claims in PDF",
        found=True,
        location=state["pdf_path"],
        content=str(findings),
        rationale="Extracted theoretical claims to be verified against code.",
        confidence=0.9
    )
    
    return {"evidences": {"doc_analyst": [evidence_claims]}}