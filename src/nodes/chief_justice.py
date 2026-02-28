import os
from src.state import AgentState, AuditReport, CriterionResult

async def chief_justice_node(state: AgentState):
    """
    Synthesizes judge opinions using deterministic conflict resolution rules.
    Satisfies rubric: Security Supremacy, Fact Supremacy, and TechLead Weighting.
    """
    criteria_results = []
    rubric_dimensions = state.get("rubric_dimensions", [])
    
    # Map opinions to criteria
    opinions_by_criterion = {}
    for op in state.get("opinions", []):
        opinions_by_criterion.setdefault(op.criterion_id, []).append(op)

    # Fact-checking: Extract valid IDs from the aggregator
    brief = state.get("aggregated_brief")
    valid_evidence_ids = {e["id"] for e in brief.evidences} if brief else set()

    for dim in rubric_dimensions:
        crit_id = dim["id"]
        crit_name = dim["name"]
        judge_ops = opinions_by_criterion.get(crit_id, [])

        if not judge_ops:
            continue

        # 1. Base Score calculation (Average)
        scores = [o.score for o in judge_ops]
        final_score = round(sum(scores) / len(scores))
        
        # 2. RULE: Variance Dissent
        variance = max(scores) - min(scores)
        dissent = f"High variance ({variance}) detected between judges." if variance > 2 else None

        # 3. RULE: Security Supremacy (Prosecutor Overrides)
        prosecutor = next((o for o in judge_ops if o.judge == "Prosecutor"), None)
        if prosecutor and "security" in prosecutor.argument.lower() and prosecutor.score <= 2:
            final_score = min(final_score, 2)
            dissent = (dissent or "") + " [SECURITY OVERRIDE APPLIED]"

        # 4. RULE: Fact Supremacy (Hallucination Penalization)
        for o in judge_ops:
            if not set(o.cited_evidence).issubset(valid_evidence_ids):
                final_score = min(final_score, 1)
                dissent = (dissent or "") + f" [FACT PENALTY: {o.judge} cited non-existent evidence]"

        # 5. RULE: Architecture Weight (TechLead Preference)
        tech_lead = next((o for o in judge_ops if o.judge == "TechLead"), None)
        if tech_lead and tech_lead.score >= 4:
            final_score = max(final_score, tech_lead.score)

        # 6. Specific Remediation Logic
        remediation_path = "No immediate action required."
        if final_score < 4:
            # Extract mentions of files or logic from the prosecutor or tech lead
            specific_concerns = prosecutor.argument if prosecutor else "Review logic."
            remediation_path = f"REF FILE: {crit_name}. ACTION: {specific_concerns}"
        
        # 7. RULE: Excellence Burden (Prevent Blind Consensus)
        if variance <= 1 and all(s >= 4 for s in scores):
            total_citations = sum(len(o.cited_evidence) for o in judge_ops)
            if total_citations < 2:
                dissent = (dissent or "") + " [EXCELLENCE BURDEN: High score with limited citation depth]"

                criteria_results.append(CriterionResult(
                    dimension_id=crit_id,
                    dimension_name=crit_name,
                    final_score=final_score,
                    judge_opinions=judge_ops,
                    dissent_summary=dissent,
                    remediation=remediation_path
                ))

    overall_score = sum(r.final_score for r in criteria_results) / max(len(criteria_results), 1)
    
    report = AuditReport(
        repo_url=state.get("repo_url", ""),
        executive_summary=f"Audit complete. Overall quality: {overall_score:.2f}/5.0.",
        overall_score=overall_score,
        criteria=criteria_results,
        remediation_plan="Implement the per-criterion remediation steps provided below."
    )

    # Production requirement: write to file
    write_markdown_report(report)

    return {"final_report": report}

def write_markdown_report(report: AuditReport):
    """Writes a structured Markdown report to the artifacts directory."""
    md_content = [
        "# Forensic Audit Report",
        f"**Repository:** {report.repo_url}",
        f"**Overall Score:** {report.overall_score:.2f}/5.0",
        "## Executive Summary",
        report.executive_summary,
        "---",
        "## Detailed Criterion Analysis"
    ]

    for c in report.criteria:
        md_content.append(f"### {c.dimension_name} (Score: {c.final_score})")
        for op in c.judge_opinions:
            md_content.append(f"- **{op.judge}**: {op.argument} (Cited: {', '.join(op.cited_evidence)})")
        if c.dissent_summary:
            md_content.append(f"> ⚖️ **Dissent:** {c.dissent_summary}")
        md_content.append(f"**Remediation:** {c.remediation}\n")

    md_content.append("## Remediation Plan")
    md_content.append(report.remediation_plan)

    os.makedirs("report_onself_generated", exist_ok=True)
    with open("report_onself_generated/audit_report.md", "w", encoding="utf-8") as f:
        f.write("\n\n".join(md_content))

#https://github.com/eyor-gech/Automaton-Auditor