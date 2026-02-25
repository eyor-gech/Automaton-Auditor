import os
import tempfile
import ast
from git import Repo

def clone_repo_sandboxed(repo_url: str) -> str:
    """Clones a repo into a temp directory to avoid workspace pollution."""
    tmp_dir = tempfile.mkdtemp()
    try:
        Repo.clone_from(repo_url, tmp_dir)
        return tmp_dir
    except Exception as e:
        raise RuntimeError(f"Forensic Violation: Could not clone {repo_url}. Error: {e}")

def analyze_graph_parallelism(file_path: str) -> bool:
    """Uses AST to find parallel add_edge calls: .add_edge(START, ['node1', 'node2'])"""
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for .add_edge or .add_conditional_edges
                if hasattr(node.func, 'attr') and node.func.attr in ['add_edge', 'add_conditional_edges']:
                    # In LangGraph, passing a list as the second arg indicates fan-out
                    if len(node.args) > 1 and isinstance(node.args[1], ast.List):
                        return True
        return False
    except Exception:
        return False

def get_git_history(repo_path: str):
    """Verifies the 'Git Narrative' through commit messages."""
    try:
        repo = Repo(repo_path)
        return [f"{c.committed_datetime} - {c.message.strip()}" for c in repo.iter_commits()]
    except Exception:
        return []