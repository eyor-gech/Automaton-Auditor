import asyncio
import os
import json
from dotenv import load_dotenv
from src.graph import graph
import nest_asyncio

load_dotenv()
nest_asyncio.apply()

async def run_custom_audit():
    # Load rubric
    with open("rubric.json", "r") as f:
        rubric_data = json.load(f)
    
    initial_input = {
        "repo_url": "https://github.com/Sanoy24/trp1-automation-auditor",
        "pdf_path": "./peer_repo/reports/final_report.pdf",
        "rubric_dimensions": rubric_data.get("dimensions", []),
        "evidences": [],
        "opinions": [],
        "aggregated_brief": None,
        "final_report": None
    }

    print("⚖️  SUPREME COURT SESSION COMMENCED")
    print("="*50)

    final_state = None
    async for event in graph.astream(initial_input, stream_mode="updates"):
        for node_name, state_update in event.items():
            final_state = state_update
            print(f"\n[NODE COMPLETED]: {node_name.upper()}")

    # Output evidence_log.json
    if final_state and "aggregated_brief" in final_state and final_state["aggregated_brief"]:
        brief = final_state["aggregated_brief"]
        # Save to evidence_log.json
        evidence_dict = {}
        if hasattr(brief, 'model_dump'):
            evidence_dict = brief.model_dump()
        else:
            evidence_dict = brief
        with open("evidence_log.json", "w", encoding="utf-8") as f:
            json.dump(evidence_dict, f, indent=2)
        print("✅ Saved evidence_log.json")

    # Output reports/peer_review_v1.md
    if final_state and "final_report" in final_state and final_state["final_report"]:
        report = final_state["final_report"]
        
        # Format it as markdown
        md_lines = []
        md_lines.append(f"# Full Forensic Audit Report")
        md_lines.append(f"**Overall Score:** {getattr(report, 'overall_score', 'N/A')} / 5.0")
        md_lines.append("\n## Executive Summary")
        md_lines.append(getattr(report, 'executive_summary', 'N/A'))
        md_lines.append("\n## Dimensions Evaluation")
        
        criteria = getattr(report, 'criteria', [])
        for crit in criteria:
            md_lines.append(f"\n### {getattr(crit, 'dimension_name', 'Unknown')} - Score: {getattr(crit, 'final_score', 'N/A')}/5")
            
            dissent = getattr(crit, 'dissent_summary', None)
            if dissent:
                md_lines.append(f"**Dissent Summary:** {dissent}\n")
                
            ops = getattr(crit, 'judge_opinions', [])
            for op in ops:
                md_lines.append(f"- **{getattr(op, 'judge', 'Judge')}** ({getattr(op, 'score', 'N/A')}/5): {getattr(op, 'argument', '')}")
                citations = getattr(op, 'cited_evidence', [])
                if citations:
                    md_lines.append(f"  *Citations:* {', '.join(citations)}")

        md_lines.append("\n## Strategic Remediation Plan")
        md_lines.append(getattr(report, 'remediation_plan', 'None provided'))
        
        os.makedirs("reports", exist_ok=True)
        with open("reports/peer_review_v1.md", "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        print("✅ Saved reports/peer_review_v1.md")
    else:
        print("❌ Final report not found in final state.")

if __name__ == "__main__":
    asyncio.run(run_custom_audit())
