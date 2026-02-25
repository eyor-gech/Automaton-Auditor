import os
import re
import shutil
import tempfile
import ast
from contextlib import contextmanager
from git import Repo, GitCommandError, InvalidGitRepositoryError

# -----------------------------
# URL VALIDATION
# -----------------------------

GIT_URL_REGEX = re.compile(
    r"^(https:\/\/|git@)([\w\.@]+)(\/|:)([\w,\-,\_]+\/[\w,\-,\_]+)(\.git)?$"
)

def validate_git_url(repo_url: str) -> bool:
    return bool(GIT_URL_REGEX.match(repo_url))


# -----------------------------
# SANDBOX LIFECYCLE MANAGEMENT
# -----------------------------

@contextmanager
def clone_repo_sandboxed(repo_url: str):
    """
    Context-managed sandbox clone.
    Auto-cleans directory after use.
    """
    if not validate_git_url(repo_url):
        raise ValueError(f"Invalid Git URL format: {repo_url}")

    tmp_dir = tempfile.mkdtemp(prefix="audit_sandbox_")

    try:
        repo = Repo.clone_from(repo_url, tmp_dir)
        yield tmp_dir
    except GitCommandError as e:
        raise RuntimeError(
            f"[GIT ERROR] Clone failed.\n"
            f"Command: {e.command}\n"
            f"Status: {e.status}\n"
            f"StdErr: {e.stderr}"
        )
    except Exception as e:
        raise RuntimeError(f"[SYSTEM ERROR] Unexpected cloning issue: {str(e)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# -----------------------------
# PARALLELISM AST ANALYSIS
# -----------------------------

def analyze_graph_parallelism(file_path: str) -> bool:
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'attr') and node.func.attr in [
                    'add_edge',
                    'add_conditional_edges'
                ]:
                    if len(node.args) > 1 and isinstance(node.args[1], ast.List):
                        return True
        return False
    except Exception:
        return False


# -----------------------------
# STRUCTURED GIT HISTORY
# -----------------------------

def get_git_history(repo_path: str):
    try:
        repo = Repo(repo_path)
        return [
            {
                "hash": c.hexsha,
                "author": c.author.name,
                "date": c.committed_datetime.isoformat(),
                "message": c.message.strip()
            }
            for c in repo.iter_commits()
        ]
    except InvalidGitRepositoryError:
        return {"error": "Invalid Git repository."}
    except Exception as e:
        return {"error": str(e)}