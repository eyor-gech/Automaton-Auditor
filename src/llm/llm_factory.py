# src/llm/llm_factory.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from pydantic import BaseModel

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # ollama | gemini
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

def get_llm():
    """
    Centralized LLM factory.
    Modify here to affect all nodes globally.
    """

    if LLM_PROVIDER == "gemini":
        return ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=LLM_TEMPERATURE
        )

    if LLM_PROVIDER == "ollama":
        return ChatOllama(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def get_structured_llm(schema: BaseModel):
    """
    Returns LLM bound to Pydantic schema.
    Enforces structured output.
    """
    llm = get_llm()
    return llm.with_structured_output(schema)