import os
from typing import Type
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from pydantic import BaseModel

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

def get_llm(is_structured: bool = False):
    """
    Centralized LLM factory with provider-specific configurations.
    """
    if LLM_PROVIDER == "gemini":
        return ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=LLM_TEMPERATURE
        )

    if LLM_PROVIDER == "ollama":
        # Master Thinker: Use format="json" for local models to ensure reliability
        return ChatOllama(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            format="json" if is_structured else None
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")

def get_structured_llm(schema: Type[BaseModel]):
    """
    Returns LLM bound to Pydantic schema. 
    Uses provider-specific binding methods for maximum reliability.
    """
    if LLM_PROVIDER == "gemini":
        llm = get_llm(is_structured=True)
        return llm.with_structured_output(schema)
    
    if LLM_PROVIDER == "ollama":
        # For Ollama, we use the model with JSON formatting and clear instructions
        llm = get_llm(is_structured=True)
        return llm.with_structured_output(schema)
    
    return get_llm().with_structured_output(schema)