"""Marketing tools: ad_planner, compliance_check, and get_campaign (campaign DB lookup)."""

import json
from pathlib import Path
from typing import Any

from marketing_agent import config as agent_config


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


def get_campaign(category: str = "", industry: str = "", **kwargs: Any) -> dict[str, Any]:
    """Look up an ad campaign by category or industry from the campaigns database.

    Input: category (e.g. 'healthcare') or industry (alias for category).
    Output: campaign record with id, name, description, image_url (for frontend to display the creative).
    """
    path = getattr(agent_config, "CAMPAIGNS_JSON_PATH", None)
    if path is None:
        return {
            "status": "error",
            "message": "Campaigns database not configured.",
            "campaign": None,
        }
    path = Path(path)
    if not path.exists():
        return {
            "status": "error",
            "message": "Campaigns database not found.",
            "campaign": None,
        }
    query = str(category or industry or "").strip().lower()
    if not query:
        return {
            "status": "error",
            "message": "Please specify category or industry (e.g. healthcare).",
            "campaign": None,
        }
    try:
        with open(path, "r", encoding="utf-8") as f:
            campaigns = json.load(f)
    except Exception as e:
        return {"status": "error", "message": str(e), "campaign": None}
    for c in campaigns:
        cat = (c.get("category") or "").lower()
        if cat and (query in cat or cat in query):
            campaign_id = c.get("id", "")
            image_path = c.get("image_path", "")
            image_url = f"/api/campaigns/{campaign_id}/image" if campaign_id and image_path else ""
            return {
                "status": "ok",
                "campaign": {
                    "id": campaign_id,
                    "category": c.get("category"),
                    "name": c.get("name", ""),
                    "description": c.get("description", ""),
                    "image_path": image_path,
                    "image_url": image_url,
                },
            }
    return {
        "status": "not_found",
        "message": f"No campaign found for category/industry: {query}",
        "campaign": None,
    }
