# src/nodes/aggregator.py
import os
from src.state import AgentState, Evidence
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

async def aggregator_node(state: AgentState):
    """
    Collects all detective evidence, cross-validates, and flags hallucinations.
    Produces 'aggregated_brief' for judges.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_AGGREGATOR_KEY")
    )

    findings = state.get("evidences", {})

    prompt = f"""
    You are the Evidence Aggregator.
    Review all detective findings: {findings}.
    Tasks:
    1. Identify any hallucinated claims (non-existent files or unsupported assertions).
    2. Consolidate valid facts with evidence ids.
    3. Return JSON object:
       {{
           "evidences": [{{"id": evidence_id, "source": source, "fact": fact}}]
       }}
    """

    res = await llm.ainvoke(prompt)

    return {
        "aggregated_brief": res.content,
        "status": "EVIDENCE_SYNCHRONIZED"
    }