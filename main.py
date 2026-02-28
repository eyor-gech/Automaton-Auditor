import asyncio
import argparse
import json
import os
from dotenv import load_dotenv
from src.graph import graph
import nest_asyncio
import traceback

load_dotenv()
nest_asyncio.apply()

async def run_forensic_audit(repo_url: str, pdf_path: str):
    """
    Full Supreme Court Audit Execution.
    Streams detectives → judges → chief reasoning.
    Fully error-tolerant, continues even if a node fails.
    """
    try:
        with open("rubric.json", "r", encoding="utf-8") as f:
            rubric = json.load(f)
    except Exception as e:
        print("❌ Failed to load rubric.json:", e)
        return

    initial_input = {
        "repo_url": repo_url,
        "pdf_path": pdf_path,
        "rubric_dimensions": rubric.get("dimensions", []),
        "evidences": [],
        "opinions": [],
        "aggregated_brief": None
    }

    os.makedirs("report_onself_generated", exist_ok=True)

    print("\n⚖️  SUPREME COURT SESSION COMMENCED")
    print("=" * 60)

    try:
        async for event in graph.astream(initial_input, stream_mode="updates"):
            for node_name, state_update in event.items():
                print(f"\n[NODE COMPLETED]: {node_name.upper()}")
                try:
                    # Detectives
                    if node_name == "repo_investigator":
                        print("   🔍 Repo AST evidence collected.")

                    if node_name == "doc_analyst":
                        print("   📄 PDF claims extracted.")

                    if node_name == "vision_inspector":
                        print("   🖼️ Diagram inspection completed.")

                    if node_name == "aggregator":
                        brief = state_update.get("aggregated_brief")
                        if brief:
                            evidences = getattr(brief, "evidences", [])
                            flags = getattr(brief, "hallucination_flags", [])
                            print(f"   📊 Aggregated {len(evidences)} evidence items.")
                            if flags:
                                print(f"   🚨 Hallucinations flagged: {len(flags)}")
                            # Dump evidence_log.json
                            try:
                                with open("evidence_log.json", "w", encoding="utf-8") as f:
                                    json.dump([e.model_dump() if hasattr(e, "model_dump") else e.dict() if hasattr(e, "dict") else e for e in evidences], f, indent=2)
                            except Exception as json_err:
                                print("⚠️ Failed to write evidence_log.json:", json_err)

                    # Judges
                    if node_name in ["prosecutor", "defense", "tech_lead"]:
                        opinions = state_update.get("opinions", [])
                        if opinions:
                            last_op = opinions[-1]
                            print(f"   👨‍⚖️ {last_op.judge} Score: {last_op.score}/5 Cited: {last_op.cited_evidence}")

                    # Chief Justice
                    if node_name == "chief":
                        report = state_update.get("final_report")
                        if report:
                            print("\n" + "═" * 60)
                            print(f"🏛️  FINAL VERDICT: {report.overall_score:.2f} / 5.0")
                            print(f"📝 SUMMARY: {report.executive_summary[:100]}...")
                            print("═" * 60)
                            # Write Markdown output safely
                            try:
                                with open("report_onself_generated/audit_report.md", "w", encoding="utf-8") as f:
                                    f.write(report_to_markdown(report))
                            except Exception as e:
                                print("⚠️ Failed to write Markdown report:", e)
                except Exception as node_err:
                    print(f"   ❌ Error processing node {node_name}: {node_err}")

    except Exception as e:
        print("\n❌ Audit failed mid-execution:")
        traceback.print_exc()

    print("\n✅ Audit complete. Markdown report at report_onself_generated/audit_report.md")


def report_to_markdown(report):
    """
    Converts AuditReport object to Markdown string safely.
    """
    md = [
        "# Supreme Court Forensic Audit Report",
        f"**Repository:** `{report.repo_url}`",
        f"**Overall Score:** {getattr(report, 'overall_score', 0):.2f}/5.0",
        "## Executive Summary",
        getattr(report, "executive_summary", "No summary available."),
        "---",
        "## Detailed Criterion Analysis"
    ]

    for c in getattr(report, "criteria", []):
        md.append(f"### {c.dimension_name} (Score: {getattr(c, 'final_score', 0)})")
        for op in getattr(c, "judge_opinions", []):
            cited = ", ".join(getattr(op, "cited_evidence", []))
            md.append(f"- **{getattr(op, 'judge', 'Unknown')}**: {getattr(op, 'argument', '')} (Cited: {cited})")
        dissent = getattr(c, "dissent_summary", None)
        if dissent:
            md.append(f"> ⚖️ **Dissent:** {dissent}")
        md.append(f"**Remediation:** {getattr(c, 'remediation', 'No action required.')}\n")

    md.append("## Remediation Plan")
    md.append(getattr(report, "remediation_plan", "No remediation needed."))

    return "\n\n".join(md)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()

    try:
        asyncio.run(run_forensic_audit(args.repo, args.pdf))
    except KeyboardInterrupt:
        print("\n⚠️ Audit interrupted by user.")
    except Exception as e:
        print("\n❌ Unexpected fatal error:")
        traceback.print_exc()