"""LLM backends: abstract interface and implementations."""

from marketing_agent.llm.base import BaseLLM
from marketing_agent.llm.huggingface import HuggingFaceLLM
from marketing_agent.llm.openai import OpenAILLM

__all__ = ["BaseLLM", "HuggingFaceLLM", "OpenAILLM"]


def get_llm(backend: str | None = None):
    """Factory: return LLM instance for configured backend."""
    from marketing_agent import config

    backend = backend or config.LLM_BACKEND
    if backend == "openai":
        return OpenAILLM()
    return HuggingFaceLLM()
