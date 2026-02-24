"""Marketing tools: ad_planner and compliance_check (placeholders)."""

from typing import Any


def ad_planner(
    keywords: str = "",
    product_info: str = "",
    budget_total: float | None = None,
    objectives: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    """Placeholder: recommend platforms, ad formats, budget allocation, pacing.

    Input: keywords, product_info, budget_total, objectives.
    Output: platform/formats suggestions and budget draft (stub).
    """
    return {
        "status": "stub",
        "message": "ad_planner is a placeholder; implement with LLM or rules.",
        "suggestions": {
            "platforms": ["Meta", "Google", "TikTok", "Amazon"],
            "formats": ["Search", "Display", "Video"],
            "budget_allocation": {},
            "pacing": "test_then_scale",
        },
        "inputs": {
            "keywords": keywords,
            "product_info": product_info[:200] if product_info else "",
            "budget_total": budget_total,
            "objectives": objectives[:200] if objectives else "",
        },
    }


def compliance_check(content: str = "", **kwargs: Any) -> dict[str, Any]:
    """Placeholder: check draft copy or plan for policy violations and risks.

    Input: content (draft text or plan).
    Output: violations and risk hints (stub).
    """
    return {
        "status": "stub",
        "message": "compliance_check is a placeholder; implement with RAG + LLM.",
        "violations": [],
        "risks": [],
        "content_preview": (content[:300] + "...") if len(content) > 300 else content,
    }
