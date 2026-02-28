from src.state import AgentState, AggregatedBrief
from src.llm.llm_factory import get_structured_llm

async def aggregator_node(state: AgentState):
    """Collects evidence, cross-validates, and prevents judge hallucination."""
    structured_llm = get_structured_llm(AggregatedBrief)
    
    evidences_raw = [e.dict() for e in state.get("evidences", [])]
    
    prompt = f"""
    Review the following forensic evidence collected by detectives:
    {evidences_raw}

    1. Cross-reference claims.
    2. Flag any internal contradictions or unsupported claims as 'hallucination_flags'.
    3. Return a clean, consolidated list of evidence for the Judicial layer.
    """
    
    brief = await structured_llm.ainvoke(prompt)
    return {"aggregated_brief": brief}