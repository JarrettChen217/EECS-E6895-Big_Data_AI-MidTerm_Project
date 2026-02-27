"""Router: intent classification -> JSON plan."""

from __future__ import annotations

from typing import Any

from marketing_agent.llm.base import BaseLLM
from marketing_agent.agent.utils import extract_json

try:
    from prompts.router import make_router_prompt, ROUTER_SYSTEM
except ImportError:
    # Log warning if prompts.router is not found.
    print("Warning: prompts.router not found, using default router system.")

    ROUTER_SYSTEM = "Output strictly valid JSON only. No extra text."

    def make_router_prompt(question: str) -> str:
        return f"""Return valid JSON: {{"plan": [{{"tool": "...", "args": {{...}}}}]}}.
User question: {question}
JSON:"""


def route_question(question: str, llm: BaseLLM) -> dict[str, Any]:
    """Classify intent and return plan = {"plan": [{"tool", "args"}, ...]}."""
    router_text = make_router_prompt(question)
    messages = [
        {"role": "system", "content": ROUTER_SYSTEM},
        {"role": "user", "content": router_text},
    ]
    raw = llm.generate(messages, max_new_tokens=256, temperature=0.0)
    try:
        plan = extract_json(raw)
        if "plan" not in plan or not isinstance(plan["plan"], list) or len(plan["plan"]) == 0:
            raise ValueError("Invalid plan schema")
        return plan
    except Exception:
        # Fallback: RAG only
        return {"plan": [{"tool": "rag", "args": {"question": question, "k": 3}}]}
