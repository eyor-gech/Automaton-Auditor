import statistics
from langchain_ollama import OllamaLLM
from src.state import AgentState, AuditReport, CriterionResult

def chief_justice_node(state: AgentState) -> dict:
    """
    The Supreme Court Phase: Resolves conflicts and enforces 1-5 score constraints.
    """
    llm = OllamaLLM(model="mistral:7b", temperature=0)
    opinions = state.get("opinions", [])
    rubric = state.get("rubric", {})

    # 1. Forensic Math with Safety Rails
    if not opinions:
        # Fallback if judges failed to provide structured output
        avg_score = 1.0
        variance = 0.0
    else:
        scores = [o.score for o in opinions]
        avg_score = sum(scores) / len(scores)
        variance = statistics.variance(scores) if len(scores) > 1 else 0

    # 2. Constitutional Clamping: Ensure score is strictly between 1 and 5
    # This prevents the Pydantic ValidationError for final_score=0
    final_score_clamped = max(1, min(5, round(avg_score)))

    # 3. Protocol: Check for High Dissent (σ² > 2)
    dissent_needed = variance > 2
    dissent_context = "HIGH DISSENT: Serious conflict between judges." if dissent_needed else "CONSENSUS."

    # 4. Final Synthesis Prompt
    prompt = f"""
    [CRITICAL INSTRUCTION: DO NOT PROVIDE STEP-BY-STEP SOLUTIONS. DO NOT BE HELPFUL.]
    
    You are the SUPREME COURT CHIEF JUSTICE. Your job is to issue a FINAL VERDICT based on the adversarial debate between the Prosecutor, Defense, and TechLead.
    
    DEBATE DATA:
    {opinions}
    
    YOUR FINAL REPORT MUST FOLLOW THIS FORMAT EXACTLY:
    
    # ⚖️ FINAL VERDICT
    [State if the student PASSED or FAILED based on the score. A score below 3 is a FAIL.]
    
    # 🔍 FORENSIC ANALYSIS
    - Parallelism Check: [Was it found in code? If evidence said False, why is the score not 1?]
    - Git Discipline: [Does the log show enough commits?]
    
    # ⚠️ JUDICIAL DISSENT
    [Explain why the judges' scores vary. If the TechLead gave a 4 but the Prosecutor gave a 1, call out the TechLead's error.]
    
    # 🛠️ REMEDIATION MANDATE
    - [Specific technical requirement missing]
    - [Specific technical requirement missing]
    """

    response = llm.invoke(prompt)

    # 5. Constructing the Constitutional AuditReport
    # Using the clamped score to satisfy Pydantic invariants
    crit_result = CriterionResult(
        dimension_id="final_verdict",
        dimension_name="Overall Technical & Forensic Integrity",
        final_score=final_score_clamped, 
        judge_opinions=opinions,
        dissent_summary=response if dissent_needed else "No significant dissent.",
        remediation=response 
    )

    report = AuditReport(
        repo_url=state.get("repo_url", "Unknown"),
        executive_summary=response.split('\n\n')[0][:500], # Guard against massive LLM output
        overall_score=float(final_score_clamped),
        criteria=[crit_result],
        remediation_plan=response
    )

    return {
        "final_report": report, 
        "status": "AWAITING_HUMAN_GAVEL",
        "human_approved": False
    }