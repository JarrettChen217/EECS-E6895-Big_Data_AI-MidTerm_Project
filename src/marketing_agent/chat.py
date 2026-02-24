"""Multi-turn chat using the configured LLM (optional, for API)."""

from typing import List

from marketing_agent.llm import get_llm
from marketing_agent.llm.base import BaseLLM


def chat(
    user_input: str,
    history: List[dict[str, str]],
    llm: BaseLLM | None = None,
) -> str:
    """Append user message, generate reply, append assistant message to history; return reply."""
    llm = llm or get_llm()
    history.append({"role": "user", "content": user_input})
    reply = llm.generate(
        history,
        max_new_tokens=256,
        temperature=0.7,
    )
    history.append({"role": "assistant", "content": reply})
    return reply
