import os
import re
import shutil
import tempfile
import ast
from contextlib import contextmanager
from git import Repo, GitCommandError

GIT_URL_REGEX = re.compile(r"^(https:\/\/|git@)([\w\.@]+)(\/|:)([\w,\-,\_]+\/[\w,\-,\_]+)(\.git)?$")

def validate_git_url(repo_url: str) -> bool:
    return bool(GIT_URL_REGEX.match(repo_url))

@contextmanager
def clone_repo_sandboxed(repo_url: str):
    """Secure context manager for temporary repo cloning."""
    if not validate_git_url(repo_url):
        raise ValueError(f"Invalid Git URL format: {repo_url}")
    tmp_dir = tempfile.mkdtemp(prefix="audit_sandbox_")
    try:
        Repo.clone_from(repo_url, tmp_dir, depth=1)
        yield tmp_dir
    except GitCommandError as e:
        raise RuntimeError(f"Git Clone Failed: {e.stderr}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

def analyze_repo_complexity(repo_path: str) -> dict:
    """Enriched AST Analysis: Detects Parallelism, Pydantic usage, and State patterns."""
    stats = {"parallel_wiring": False, "pydantic_models": 0, "state_reducers": 0}
    
    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith(".py"): continue
            try:
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    # Detect Parallel Edges
                    if isinstance(node, ast.Call) and hasattr(node.func, 'attr'):
                        if node.func.attr in ['add_edge', 'add_conditional_edges']:
                            if len(node.args) > 1 and isinstance(node.args[1], (ast.List, ast.Dict)):
                                stats["parallel_wiring"] = True
                    # Detect Pydantic Models
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            if hasattr(base, 'id') and base.id in ['BaseModel', 'TypedDict']:
                                stats["pydantic_models"] += 1
                    # Detect Reducers
                    if isinstance(node, ast.Subscript) and hasattr(node.value, 'id') and node.value.id == 'Annotated':
                        stats["state_reducers"] += 1
            except: continue
    return stats

def get_git_history(repo_path: str):
    """Extracts commit logs for the Defense judge to use as evidence of effort."""
    try:
        repo = Repo(repo_path)
        return [
            {
                "hash": c.hexsha[:7],
                "author": c.author.name,
                "date": c.committed_datetime.strftime("%Y-%m-%d"),
                "message": c.message.strip()
            }
            for c in repo.iter_commits()
        ]
    except Exception as e:
        return {"error": str(e)}