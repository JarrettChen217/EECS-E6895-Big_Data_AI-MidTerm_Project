"""Abstract LLM interface: generate(messages, ...) -> str."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLM(ABC):
    """Abstract base for LLM backends. Agent/RAG/Synthesizer depend only on this."""

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        max_new_tokens: int = 256,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        """Generate a single reply from a list of messages.

        Args:
            messages: List of {"role": "system"|"user"|"assistant", "content": "..."}.
            max_new_tokens: Maximum new tokens to generate.
            temperature: Sampling temperature (0 = deterministic).
            **kwargs: Backend-specific options (e.g. top_p, top_k).

        Returns:
            The assistant reply text only (no role wrapper).
        """
        ...
