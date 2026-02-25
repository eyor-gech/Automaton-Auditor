import argparse
from src.repo_tools import clone_repo_sandboxed
from src.doc_tools import ingest_pdf_content
from src.graph import graph

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()

    with clone_repo_sandboxed(args.repo) as repo_path:
        pdf_data = ingest_pdf_content(args.pdf)

        state = {
            "repo_path": repo_path,
            "pdf_data": pdf_data
        }

        result = graph.invoke(state)
        print(result)


if __name__ == "__main__":
    main()