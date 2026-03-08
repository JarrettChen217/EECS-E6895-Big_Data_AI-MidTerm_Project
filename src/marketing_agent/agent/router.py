"""Router: intent classification -> JSON plan."""

from __future__ import annotations

from typing import Any

from marketing_agent.llm.base import BaseLLM
from marketing_agent.agent.utils import extract_json

try:
    from prompts.router import make_router_prompt, ROUTER_SYSTEM, MAX_RAG_STEPS
except ImportError:
    print("Warning: prompts.router not found, using default router system.")
    ROUTER_SYSTEM = "Output strictly valid JSON only. No extra text."
    MAX_RAG_STEPS = 5

    def make_router_prompt(question: str) -> str:
        return f"""Return valid JSON with plan: platform_chooser, then 2-5 rag steps.
User question: {question}
JSON:"""


def _fallback_plan(question: str) -> dict[str, Any]:
    """Return default plan when LLM routing fails."""
    industry = question.strip()[:100] if question else "General"
    return {
        "plan": [
            {"tool": "platform_chooser", "args": {"industry": industry, "region": "US", "include_audience": True}},
            {"tool": "rag", "args": {"question": f"Meta ads policy for {industry}", "k": 3}},
            {"tool": "rag", "args": {"question": f"Google Ads policy and restricted categories for {industry}", "k": 3}},
            {"tool": "rag", "args": {"question": "TikTok ads policy and brand safety", "k": 3}},
        ]
    }


def _cap_rag_steps(plan: dict[str, Any], max_rag: int = 5) -> dict[str, Any]:
    """Cap RAG steps at max_rag; keep first platform_chooser and up to max_rag rag steps."""
    steps = plan.get("plan", [])
    if not steps:
        return plan
    try:
        from prompts.router import MAX_RAG_STEPS
        max_rag = MAX_RAG_STEPS
    except ImportError:
        pass
    chosen = []
    rag_count = 0
    for step in steps:
        tool = step.get("tool", "")
        if tool == "platform_chooser":
            chosen.append(step)
        elif tool == "rag" and rag_count < max_rag:
            chosen.append(step)
            rag_count += 1
    return {"plan": chosen}


def route_question(question: str, llm: BaseLLM) -> dict[str, Any]:
    """Return plan = {"plan": [platform_chooser, rag x N]} with LLM-extracted args (up to 5 rag steps)."""
    router_text = make_router_prompt(question)
    messages = [
        {"role": "system", "content": ROUTER_SYSTEM},
        {"role": "user", "content": router_text},
    ]
    raw = llm.generate(messages, max_new_tokens=512, temperature=0.0)
    try:
        plan = extract_json(raw)
        if "plan" not in plan or not isinstance(plan["plan"], list) or len(plan["plan"]) == 0:
            raise ValueError("Invalid plan schema")
        return _cap_rag_steps(plan)
    except Exception:
        return _fallback_plan(question)
