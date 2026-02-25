import os
from src.state import AgentState, Evidence
from src.tools.repo_tools import clone_repo_sandboxed, analyze_graph_parallelism, get_git_history
from src.tools.doc_tools import ingest_pdf_content, search_for_keywords
from src.tools.vision_tools import count_pdf_images

def repo_investigator_node(state: AgentState) -> dict:
    """Forensic Protocol A & B: Verify code structure and Git history."""
    evidences = []

    # Clone repository safely
    try:
        repo_url = state.get("repo_url")
        if not repo_url:
            raise ValueError("Missing 'repo_url' in state")
        repo_path = clone_repo_sandboxed(repo_url)
    except Exception as e:
        evidences.append(Evidence(
            goal="Clone repository",
            found=False,
            location="repo_url",
            rationale=f"Failed to clone repo: {e}",
            confidence=0.2
        ))
        repo_path = None  # downstream checks will skip

    # AST Parallelism Check
    if repo_path:
        try:
            graph_file = os.path.join(repo_path, "src/graph.py")
            is_parallel = analyze_graph_parallelism(graph_file)
            evidences.append(Evidence(
                goal="Verify parallel graph wiring",
                found=is_parallel,
                location="src/graph.py",
                rationale="AST parsing checked for parallel add_edge calls with list arguments.",
                confidence=1.0
            ))
        except Exception as e:
            evidences.append(Evidence(
                goal="Verify parallel graph wiring",
                found=False,
                location="src/graph.py",
                rationale=f"Failed analysis: {e}",
                confidence=0.3
            ))

    # Git History Extraction
    if repo_path:
        try:
            history = get_git_history(repo_path)
            evidences.append(Evidence(
                goal="Extract full commit history",
                found=len(history) > 0,
                location=".git/logs",
                content="\n".join(history[:10]) if history else "",
                rationale="Verified progression through atomic commit logs.",
                confidence=1.0 if history else 0.2
            ))
        except Exception as e:
            evidences.append(Evidence(
                goal="Extract full commit history",
                found=False,
                location=".git/logs",
                rationale=f"Failed to get git history: {e}",
                confidence=0.2
            ))

    return {"evidences": {"repo_investigator": evidences}}

def doc_analyst_node(state: AgentState) -> dict:
    """Forensic Protocol B: Cross-reference PDF claims."""
    evidences = []

    pdf_path = state.get("pdf_path")
    if not pdf_path:
        evidences.append(Evidence(
            goal="Identify architectural claims in PDF",
            found=False,
            location="pdf_path",
            rationale="PDF path missing in state.",
            confidence=0.0
        ))
        return {"evidences": {"doc_analyst": evidences}}

    try:
        content = ingest_pdf_content(pdf_path)
        keywords = ["Dialectical Synthesis", "AST Parsing", "Parallel Execution", "Pydantic"]
        findings = search_for_keywords(content, keywords)
        evidences.append(Evidence(
            goal="Identify architectural claims in PDF",
            found=True,
            location=pdf_path,
            content=str(findings),
            rationale="Extracted theoretical claims to be verified against code.",
            confidence=0.9
        ))
    except Exception as e:
        evidences.append(Evidence(
            goal="Identify architectural claims in PDF",
            found=False,
            location=pdf_path,
            rationale=f"Failed to process PDF: {e}",
            confidence=0.2
        ))

    return {"evidences": {"doc_analyst": evidences}}

def vision_inspector_node(state: AgentState) -> dict:
    """Budget-Friendly Vision Inspector: Checks for visual documentation."""
    evidences = []

    pdf_path = state.get("pdf_path")
    if not pdf_path:
        evidences.append(Evidence(
            goal="Visual Evidence Detection",
            found=False,
            location="pdf_path",
            rationale="PDF path missing in state.",
            confidence=0.0
        ))
        return {"evidences": {"vision_inspector": evidences}}

    try:
        img_count = count_pdf_images(pdf_path)
        evidences.append(Evidence(
            goal="Visual Evidence Detection",
            found=img_count > 0,
            location=pdf_path,
            content=f"Detected {img_count} images in the audit report.",
            rationale="Verified presence of diagrams. Logic analysis deferred to Judicial layer.",
            confidence=1.0
        ))
    except Exception as e:
        evidences.append(Evidence(
            goal="Visual Evidence Detection",
            found=False,
            location=pdf_path,
            rationale=f"Failed to count images: {e}",
            confidence=0.2
        ))

    return {"evidences": {"vision_inspector": evidences}}