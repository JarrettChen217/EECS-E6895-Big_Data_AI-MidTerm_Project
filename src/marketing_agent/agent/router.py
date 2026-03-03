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


# Keywords that indicate user wants a stored campaign creative (not ad_planner copy)
_CAMPAIGN_INTENT_KEYWORDS = (
    "ad", "ads", "creative", "creatives", "campaign", "image", "picture",
    "give", "want", "show", "get", "need", "example", "sample", "option",
    "concept", "can you", "could you", "help", "make", "design",
)


def _force_campaign_plan(question: str) -> dict[str, Any] | None:
    """If question clearly asks for a campaign creative for a known category, return plan without LLM."""
    q = question.strip().lower()
    # healthcare: must contain "healthcare" or ("health" + ad/creative/campaign)
    is_healthcare = "healthcare" in q or ("health" in q and any(x in q for x in ("ad", "ads", "creative", "campaign")))
    if is_healthcare:
        for kw in _CAMPAIGN_INTENT_KEYWORDS:
            if kw in q:
                return {"plan": [{"tool": "get_campaign", "args": {"category": "healthcare"}}]}
    return None


def route_question(question: str, llm: BaseLLM) -> dict[str, Any]:
    """Classify intent and return plan = {"plan": [{"tool", "args"}, ...]}."""
    forced = _force_campaign_plan(question)
    if forced is not None:
        return forced
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
