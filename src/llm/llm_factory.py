import os
import json
import re
from typing import Type
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from pydantic import BaseModel, ValidationError

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-r1:1.5b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

def get_llm(is_structured: bool = False):
    if LLM_PROVIDER == "gemini":
        return ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=LLM_TEMPERATURE
        )
    if LLM_PROVIDER == "ollama":
        return ChatOllama(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            format="json" if is_structured else None
        )
    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")

def get_structured_llm(schema: Type[BaseModel]):
    llm = get_llm(is_structured=True)

    if LLM_PROVIDER == "ollama":
        class OllamaWrapper:
            def __init__(self, llm, schema):
                self.llm = llm
                self.schema = schema

            async def ainvoke(self, prompt, **kwargs):
                try:
                    raw_output = await self.llm.ainvoke(prompt, **kwargs)
                    raw_str = raw_output.content if hasattr(raw_output, "content") else str(raw_output)

                    # FIX: Strip DeepSeek <think> tags or extra markdown bloat
                    raw_str = re.sub(r"<think>.*?</think>", "", raw_str, flags=re.DOTALL).strip()
                    raw_str = raw_str.replace("```json", "").replace("```", "").strip()

                    data = json.loads(raw_str)
                    
                    # Pydantic v2 validation
                    return self.schema.model_validate(data)

                # Inside llm_factory.py -> OllamaWrapper.ainvoke

                except (ValidationError, json.JSONDecodeError) as e:
                    print(f"⚠️ LLM parsing failed. Creating safe fallback: {e}")
                    
                    fallback_data = {}
                    for name, field in self.schema.model_fields.items():
                        # Get the underlying type of the field
                        field_type = field.annotation
                        
                        # 1. Handle Lists (evidences, hallucination_flags)
                        if getattr(field_type, "__origin__", None) is list:
                            fallback_data[name] = []
                        
                        # 2. Handle Strings (summary) - THIS FIXES YOUR ERROR
                        elif field_type is str:
                            fallback_data[name] = "No summary generated due to LLM parsing error."
                            
                        # 3. Handle Floats/Ints (scores)
                        elif field_type in [float, int]:
                            fallback_data[name] = 0.0
                            
                        # 4. Default for everything else
                        else:
                            fallback_data[name] = None
                    
                    # model_validate will now succeed because 'summary' is a string, not None
                    return self.schema.model_validate(fallback_data)

        return OllamaWrapper(llm, schema)

    # For Gemini/OpenAI
    if hasattr(llm, "with_structured_output"):
        return llm.with_structured_output(schema)
    
    return llm