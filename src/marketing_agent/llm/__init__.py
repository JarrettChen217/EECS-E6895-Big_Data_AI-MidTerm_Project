"""LLM backends: abstract interface and implementations."""

from marketing_agent.llm.base import BaseLLM
from marketing_agent.llm.huggingface import HuggingFaceLLM
from marketing_agent.llm.openai import OpenAILLM

__all__ = ["BaseLLM", "HuggingFaceLLM", "OpenAILLM", "get_llm"]

# Singleton: one LLM instance per process (lazy init on first get_llm() with backend=None).
# Use a list so we can mutate without the global keyword.
_llm_instance: list[BaseLLM | None] = [None]


def get_llm(backend: str | None = None) -> BaseLLM:
    """Return the configured LLM. Lazy singleton when backend is None (uses config.LLM_BACKEND).
    When backend is passed explicitly, returns a new instance (e.g. for tests); the default
    path is still the singleton so the app only inits once."""
    from marketing_agent import config

    chosen = backend or config.LLM_BACKEND
    if backend is not None:
        # Explicit backend: no cache (caller may want a one-off for testing).
        return OpenAILLM() if chosen == "openai" else HuggingFaceLLM()

    if _llm_instance[0] is None:
        _llm_instance[0] = OpenAILLM() if chosen == "openai" else HuggingFaceLLM()
    return _llm_instance[0]
