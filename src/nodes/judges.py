from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import PydanticOutputParser
from src.state import AgentState, JudicialOpinion, JudicialDecision # Import both

# We use the Decision model for the LLM to fill out, then map it to Opinion for the State
parser = PydanticOutputParser(pydantic_object=JudicialDecision)

def run_judicial_node(state: AgentState, judge_type: str, model: str, persona_prompt: str):
    """Universal factory for constitutional judges."""
    llm = OllamaLLM(model=model, temperature=0)
    
    prompt = f"""
    ### CONSTITUTIONAL MANDATE ###
    ou are a Forensic Auditor. 
    If the evidence does not match the rubric, you must penalize. 
    Being 'nice' is a violation of the protocol.

    ### THE LAW (RUBRIC) ###
    {state['rubric']}

    ### THE EVIDENCE ###
    {state['evidences']}

    ### TASK ###
    1. Compare the EVIDENCE directly against the RUBRIC.
    2. If the evidence shows 'Parallel: False' and the rubric demands 'Parallel: True' for a 5, you MUST give a 1.
    3. Your reasoning must be: "Evidence shows [X], but Rubric requires [Y]. Score: [Z]."

    {parser.get_format_instructions()}
    """
    
    try:
        response = llm.invoke(prompt)
        decision = parser.parse(response)
        
        # Map to the JudicialOpinion model defined in your state.py
        opinion = JudicialOpinion(
            judge=judge_type,
            criterion_id="logic_and_impl", 
            score=decision.score,
            argument=decision.reasoning,
            cited_evidence=decision.citations
        )
        return {"opinions": [opinion]}
    except Exception as e:
        return {"status": f"error_{judge_type.lower()}", "instructor_feedback": f"Parser error: {str(e)}"}

# The Three Constitutional Nodes
def prosecutor_node(state: AgentState):
    return run_judicial_node(state, "Prosecutor", "llama3.2", 
        "Strict, skeptical, and focused on missing implementation or 'vaporware' claims.")

def defense_node(state: AgentState):
    return run_judicial_node(state, "Defense", "llama3.2", 
        "Advocate for the student. Highlight intent, effort in Git logs, and partial successes.")

def tech_lead_node(state: AgentState):
    return run_judicial_node(state, "TechLead", "mistral:7b", 
        "Pragmatic engineer. Ignore the 'talk'—focus on Pydantic models, AST results, and code structure.")