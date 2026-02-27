import os
from src.state import AgentState, Evidence
from src.tools.repo_tools import clone_repo_sandboxed, analyze_repo_complexity, get_git_history
from src.tools.doc_tools import ingest_pdf_semantically, query_pdf_chunks
from src.tools.vision_tools import count_pdf_images

def repo_investigator_node(state: AgentState) -> dict:
    """Fact-finding node for the Repository using AST and Git history."""
    repo_url = state.get("repo_url")
    if not repo_url:
        return {"evidences": {"repo_investigator": []}}

    evidences = []
    try:
        with clone_repo_sandboxed(repo_url) as tmp_dir:
            stats = analyze_repo_complexity(tmp_dir)
            evidences.append(Evidence(
                goal="Technical Pattern Analysis",
                found=stats["parallel_wiring"],
                location="AST Analysis",
                content=f"Parallel: {stats['parallel_wiring']}, Models: {stats['pydantic_models']}",
                rationale="Verified code patterns for graph wiring and state management.",
                confidence=1.0
            ))

            history = get_git_history(tmp_dir)
            if isinstance(history, list):
                evidences.append(Evidence(
                    goal="Commit History Audit",
                    found=len(history) > 0,
                    location="Git Logs",
                    content=str(history[:3]),
                    rationale="Extracted commit logs for effort validation.",
                    confidence=1.0
                ))
    except Exception as e:
        evidences.append(Evidence(goal="Repo Check", found=False, location="Git", rationale=str(e), confidence=1.0))

    return {"evidences": {"repo_investigator": evidences}}

def doc_analyst_node(state: AgentState) -> dict:
    """Fact-finding node for the PDF using semantic chunking."""
    pdf_path = state.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        return {"evidences": {"doc_analyst": []}}

    evidences = []
    try:
        data = ingest_pdf_semantically(pdf_path)
        chunks = data.get("chunks", [])
        
        # Search for core architectural claims
        matches = query_pdf_chunks(chunks, "parallel")
        evidences.append(Evidence(
            goal="Identify Arch Claims",
            found=len(matches) > 0,
            location=pdf_path,
            content=matches[0]["content"] if matches else "No parallel claims found.",
            rationale="Queried semantic chunks for architectural keywords.",
            confidence=0.9
        ))
    except Exception as e:
        evidences.append(Evidence(goal="PDF Analysis", found=False, location="PDF", rationale=str(e), confidence=1.0))

    return {"evidences": {"doc_analyst": evidences}}

def vision_inspector_node(state: AgentState) -> dict:
    """Heuristic Vision: Checks for visual documentation."""
    pdf_path = state.get("pdf_path")
    try:
        img_count = count_pdf_images(pdf_path)
        return {"evidences": {"vision_inspector": [Evidence(
            goal="Visual Asset Detection", found=img_count > 0, location="PDF",
            content=f"Images: {img_count}", rationale="Checked for diagrams.", confidence=1.0
        )]}}
    except:
        return {"evidences": {"vision_inspector": []}}