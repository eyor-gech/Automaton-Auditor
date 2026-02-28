import asyncio
import os
import json
from dotenv import load_dotenv
from src.graph import graph
import nest_asyncio

# Initialize the environment
load_dotenv()
nest_asyncio.apply()

async def run_forensic_audit():
    """
    Headless execution of the Forensic Auditor.
    Demonstrates State Graph transitions and parallel fan-out.
    """
    
    # 1. Define the Initial State
    # Replace these with your actual test targets
    initial_input = {
        "repo_url": "https://github.com/langchain-ai/langgraph",#"https://github.com/example/target-repo",
        "pdf_path": "./docs/architecture_spec.pdf",#"./docs/architecture_spec.pdf",
        "rubric_dimensions": [
            {"id": "arch", "name": "Parallel Graph Architecture"},
            {"id": "state", "name": "State Reducer Safety"}
            #{"id": "history", "name": "Engineering Progression"}
        ],
        "evidences": [],
        "opinions": [],
        "aggregated_brief": None
    }

    print("⚖️  SUPREME COURT SESSION COMMENCED")
    print("="*50)

    # 2. Stream the Graph Execution
    # .astream allows us to see the parallel nodes finishing in real-time
    async for event in graph.astream(initial_input, stream_mode="updates"):
        for node_name, state_update in event.items():
            print(f"\n[NODE COMPLETED]: {node_name.upper()}")
            
            # Master Thinker Detail: Print specific node outcomes
            if node_name == "aggregator":
                count = len(state_update.get("aggregated_brief", {}).get("evidences", []))
                print(f"   📊 Aggregated {count} pieces of forensic evidence.")
            
            if node_name in ["prosecutor", "defense", "tech_lead"]:
                # Access the last opinion added to the list
                opinion = state_update.get("opinions", [])[-1]
                print(f"   👨‍⚖️ {opinion.judge} assigned score: {opinion.score}/5")

            if node_name == "chief":
                report = state_update.get("final_report")
                print("\n" + "═"*50)
                print(f"🏛️  FINAL VERDICT: {report.overall_score:.2f} / 5.0")
                print(f"📝 SUMMARY: {report.executive_summary[:100]}...")
                print("═"*50)

if __name__ == "__main__":
    try:
        asyncio.run(run_forensic_audit())
    except KeyboardInterrupt:
        print("\nCourt adjourned prematurely.")
    except Exception as e:
        print(f"\nFATAL ERROR IN AUDIT: {e}")