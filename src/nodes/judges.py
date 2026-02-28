# src/nodes/judges.py

from src.state import AgentState, JudicialOpinion
from src.llm.llm_factory import get_structured_llm

MAX_RETRIES = 2

async def run_judge(state: AgentState, name: str, persona: str):
    """
    High-tier persona-based structured judge with retry and validation.
    """

    structured_llm = get_structured_llm(JudicialOpinion)
    opinions = []

    valid_evidence_ids = {
        e["id"] for e in state.get("aggregated_brief", {}).get("evidences", [])
    }

    for dim in state.get("rubric_dimensions", []):
        crit_id = dim["id"]
        crit_name = dim["name"]

        prompt = f"""
You are acting as: {persona}

Evaluate rubric criterion:
Name: {crit_name}
ID: {crit_id}

Instructions:
- Score strictly 1–5
- Cite ONLY evidence IDs that exist
- If evidence is insufficient, penalize score
- Do not hallucinate
- Justify using adversarial reasoning appropriate to your role

Return structured JudicialOpinion.
"""

        for attempt in range(MAX_RETRIES):
            try:
                opinion = await structured_llm.ainvoke(prompt)
                opinion.judge = name

                # Validate cited evidence
                if not set(opinion.cited_evidence).issubset(valid_evidence_ids):
                    raise ValueError("Invalid evidence cited")

                opinions.append(opinion)
                break

            except Exception:
                if attempt == MAX_RETRIES - 1:
                    continue

    return {"opinions": opinions}


async def prosecutor_node(state: AgentState):
    return await run_judge(
        state,
        name="Prosecutor",
        persona="""
Adversarial security auditor.
You aggressively search for:
- Security flaws
- Missing validation
- Architectural shortcuts
- Lazy engineering decisions
You penalize undocumented assumptions.
"""
    )


async def defense_node(state: AgentState):
    return await run_judge(
        state,
        name="Defense",
        persona="""
Supportive evaluator.
You reward:
- Effort
- Iterative progress
- Creative workarounds
- Demonstrated learning
You assume good intent unless proven otherwise.
"""
    )


async def tech_lead_node(state: AgentState):
    return await run_judge(
        state,
        name="TechLead",
        persona="""
Senior pragmatic architect.
You prioritize:
- Structural correctness
- Maintainability
- Reducer safety
- Parallel graph integrity
Cosmetic flaws are low priority.
Architecture weighs most.
"""
    )