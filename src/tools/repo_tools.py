import os
import re
import shutil
import tempfile
import ast
from contextlib import contextmanager
from git import Repo, GitCommandError
import ast
from collections import defaultdict
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
    """
    Deep structural AST analysis:
    - Detect graph fan-out/fan-in topology
    - Detect reducer annotations
    - Detect Pydantic/TypedDict models
    """

    stats = {
        "parallel_wiring": False,
        "fan_out_nodes": 0,
        "fan_in_nodes": 0,
        "state_reducers": 0,
        "pydantic_models": 0
    }

    edge_map = defaultdict(list)

    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=file_path)

                for node in ast.walk(tree):

                    # Detect add_edge("A", "B")
                    if isinstance(node, ast.Call) and hasattr(node.func, "attr"):
                        if node.func.attr == "add_edge":
                            if len(node.args) >= 2:
                                src = getattr(node.args[0], "value", None)
                                dst = getattr(node.args[1], "value", None)
                                if isinstance(src, str) and isinstance(dst, str):
                                    edge_map[src].append(dst)

                        if node.func.attr == "add_conditional_edges":
                            # conditional edges count as structural routing
                            stats["parallel_wiring"] = True

                    # Detect reducer usage via Annotated[List, operator.add]
                    if isinstance(node, ast.Subscript):
                        if hasattr(node, "slice"):
                            if "Annotated" in ast.unparse(node):
                                if "operator.add" in ast.unparse(node) or "operator.ior" in ast.unparse(node):
                                    stats["state_reducers"] += 1

                    # Detect Pydantic / TypedDict models
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            base_name = getattr(base, "id", None)
                            if base_name in ["BaseModel", "TypedDict"]:
                                stats["pydantic_models"] += 1

            except Exception:
                continue

    # Compute fan-out / fan-in
    fan_in_counter = defaultdict(int)

    for src, targets in edge_map.items():
        if len(targets) > 1:
            stats["fan_out_nodes"] += 1
            stats["parallel_wiring"] = True
        for t in targets:
            fan_in_counter[t] += 1

    for node, count in fan_in_counter.items():
        if count > 1:
            stats["fan_in_nodes"] += 1

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