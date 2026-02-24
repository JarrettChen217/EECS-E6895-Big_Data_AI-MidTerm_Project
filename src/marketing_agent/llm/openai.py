"""OpenAI API LLM backend."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from marketing_agent.llm.base import BaseLLM
from marketing_agent import config as agent_config


class OpenAILLM(BaseLLM):
    """LLM using OpenAI Chat Completions API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self._client = OpenAI(api_key=api_key or agent_config.OPENAI_API_KEY)
        self.model = model or agent_config.OPENAI_MODEL

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        max_new_tokens: int = 256,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=temperature,
            **kwargs,
        )
        choice = resp.choices[0]
        return (choice.message.content or "").strip()
