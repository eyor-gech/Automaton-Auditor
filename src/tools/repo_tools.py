import os
import re
import shutil
import tempfile
import ast
from contextlib import contextmanager
from git import Repo, GitCommandError

GIT_URL_REGEX = re.compile(r"^(https:\/\/|git@)([\w\.@]+)(\/|:)([\w\-\_]+\/[\w\-\_]+)(\.git)?$")

def validate_git_url(repo_url: str) -> bool:
    return bool(GIT_URL_REGEX.match(repo_url))

@contextmanager
def clone_repo_sandboxed(repo_url: str):
    """Secure context manager for temporary repo cloning."""
    if not validate_git_url(repo_url):
        raise ValueError(f"Invalid Git URL format: {repo_url}")
    tmp_dir = tempfile.mkdtemp(prefix="audit_sandbox_")
    try:
        Repo.clone_from(repo_url, tmp_dir)  # full history needed
        yield tmp_dir
    except GitCommandError as e:
        raise RuntimeError(f"Git Clone Failed: {e.stderr}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

def analyze_repo_complexity(repo_path: str) -> dict:
    """AST Analysis: Detect Parallelism, Pydantic usage, and State patterns."""
    stats = {"parallel_wiring": False, "pydantic_models": 0, "state_reducers": 0}
    
    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith(".py"): 
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=file_path)
                
                for node in ast.walk(tree):
                    # Detect Parallel Edges: multiple downstream targets
                    if isinstance(node, ast.Call) and hasattr(node.func, 'attr'):
                        if node.func.attr in ['add_edge', 'add_conditional_edges']:
                            if len(node.args) >= 2:
                                if isinstance(node.args[1], (ast.List, ast.Tuple)):
                                    if len(node.args[1].elts) > 1:
                                        stats["parallel_wiring"] = True

                    # Detect Pydantic Models
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            base_id = getattr(base, 'id', None) or getattr(getattr(base, 'attr', None), 'id', None)
                            if base_id in ['BaseModel', 'TypedDict']:
                                stats["pydantic_models"] += 1

                    # Detect Reducers usage (Annotated + operator.add / operator.ior)
                    if isinstance(node, ast.Call) and getattr(getattr(node.func, 'attr', None), 'lower', lambda: '')() in ['add', 'ior']:
                        stats["state_reducers"] += 1

            except Exception:
                continue
    return stats

def get_git_history(repo_path: str) -> list[dict]:
    """Full chronological commit history for effort analysis."""
    try:
        repo = Repo(repo_path)
        commits = list(repo.iter_commits(rev='HEAD', reverse=True))  # oldest first
        return [
            {
                "index": idx,
                "hash": c.hexsha[:7],
                "author": c.author.name,
                "date": c.committed_datetime.isoformat(),
                "message": c.message.strip()
            } for idx, c in enumerate(commits)
        ]
    except Exception as e:
        return [{"error": str(e)}]