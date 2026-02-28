from src.state import AgentState, AggregatedBrief, Evidence
from src.llm.llm_factory import get_structured_llm
from typing import List

# -----------------------------
# Cross-Detective Validation
# -----------------------------
def cross_validate_evidence(evidences: List[Evidence]) -> List[Evidence]:
    """
    Compare RepoInvestigator vs DocAnalyst outputs.
    Flags unsupported claims or hallucinations.
    """
    repo_evidence = [e for e in evidences if e.source == "RepoInvestigator"]
    doc_evidence = [e for e in evidences if e.source == "DocAnalyst"]

    flags: List[Evidence] = []

    # Repo claims not supported by documentation
    if repo_evidence and not doc_evidence:
        flags.append(
            Evidence(
                id="EV-CROSS-1",
                source="CrossValidator",
                goal="Detect undocumented architectural claims",
                fact="Repository contains structural claims not backed by documentation.",
                confidence=0.85,
                location=None,
                rationale="Repo evidence exists but no documentation evidence supports it."
            )
        )

    return flags

# -----------------------------
# Aggregator Node
# -----------------------------
async def aggregator_node(state: AgentState):
    """
    1️⃣ Collects all detective evidences
    2️⃣ Performs cross-detective validation
    3️⃣ Uses structured LLM to generate AggregatedBrief
    """
    # Collect all raw evidence
    evidences: List[Evidence] = state.get("evidences", [])

    # Cross-validation flags
    cross_flags = cross_validate_evidence(evidences)

    # Combine original + validation flags
    combined_evidences = evidences + cross_flags

    # Convert to dict for LLM consumption
    evidences_raw = [e.dict() for e in combined_evidences]

    # Instantiate structured LLM bound to AggregatedBrief
    structured_llm = get_structured_llm(AggregatedBrief)

    prompt = f"""
    You are an expert forensic aggregator.

    Review the following forensic evidence collected by detectives:
    {evidences_raw}

    Tasks:
    1. Cross-reference claims.
    2. Flag any internal contradictions or unsupported claims as 'hallucination_flags'.
    3. Return a clean, consolidated list of evidence for the Judicial layer.
    4. Ensure the output matches the AggregatedBrief schema exactly.
    """

    # Generate structured AggregatedBrief
    brief: AggregatedBrief = await structured_llm.ainvoke(prompt)

    return {"aggregated_brief": brief, "evidences": combined_evidences}