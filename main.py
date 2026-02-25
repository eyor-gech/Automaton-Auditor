import asyncio
import argparse
from src.graph import graph

async def run_audit(repo: str, pdf: str):
    inputs = {
        "repo_url": repo,
        "pdf_path": pdf,
        "evidences": {},
        "opinions": []
    }
    async for event in graph.astream(inputs):
        print(f"\n[NODE]: {list(event.keys())[0]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()
    asyncio.run(run_audit(args.repo, args.pdf))