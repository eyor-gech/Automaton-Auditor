import sys
import os

# Ensure the project root is on the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from src.graph import graph


async def run_test(repo_url, pdf_path):
    print(f"\n--- Testing Scenario: {repo_url} ---")
    
    # Initialize state
    initial_state = {
        "repo_url": repo_url,
        "pdf_path": pdf_path,
        "rubric_dimensions": [], # Will be used by judges later
        "evidences": {},
        "opinions": []
    }
    
    # Run the graph
    # Using 'stream' lets us see the parallel execution in real-time
    async for output in graph.astream(initial_state):
        for key, value in output.items():
            print(f"\nNode '{key}' completed.")
            if "evidences" in value:
                # Show what the detectives found
                for source, ev_list in value["evidences"].items():
                    for ev in ev_list:
                        status = "✅" if ev.found else "❌"
                        print(f"  {status} {ev.goal}: {ev.rationale[:100]}...")

if __name__ == "__main__":
    # Scenario A: A non-existent repo to test Error Handling
    #print("RUNNING SCENARIO A: THE BROKEN LINK")
    #asyncio.run(run_test("https://github.com/this/does-not-exist-123", "dummy.pdf"))
    
    # Scenario B: Your own repo to test Parallelism Detection
    # (Assuming you are in your project root)
    print("\nRUNNING SCENARIO B: THE ACTUAL REPO")
    # You can use a local path or your actual git URL here
    asyncio.run(run_test("https://github.com/eyor-gech/Automaton-Auditor", r"C:\Users\Eyor.G\Downloads\Implementation Report_Roo Code AI Native.pdf"))