"""Platform chooser tool: load benchmark data for platform comparison and decision support."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from marketing_agent import config as agent_config


def _normalize(s: str) -> str:
    """Normalize string for fuzzy matching: lowercase, collapse spaces, remove special chars."""
    s = (s or "").strip().lower()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _industry_matches(query: str, industry: str) -> bool:
    """Check if query matches industry (substring or token overlap)."""
    q = _normalize(query)
    ind = _normalize(industry)
    if not q:
        return True
    if q in ind or ind in q:
        return True
    q_tokens = set(q.split())
    ind_tokens = set(ind.split())
    return bool(q_tokens & ind_tokens)


def _load_csv(path: Path) -> list[dict[str, Any]]:
    """Load CSV into list of dicts."""
    rows = []
    if not path.exists():
        return rows
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()})
    return rows


def _filter_by_region(rows: list[dict[str, Any]], region: str) -> list[dict[str, Any]]:
    """Filter rows by Region (US, Global, or any)."""
    if not region:
        return rows
    r = str(region).strip().upper()
    if r in ("US", "USA", "UNITED STATES"):
        return [row for row in rows if (row.get("Region") or "").upper() in ("US", "USA")]
    if r in ("GLOBAL", "GLOBAL_Average"):
        return [row for row in rows if (row.get("Region") or "").upper() in ("GLOBAL", "GLOBAL_AVERAGE", "")]
    return [row for row in rows if _normalize(str(row.get("Region", ""))) == _normalize(region)]


def _filter_by_industry(rows: list[dict[str, Any]], industry: str) -> list[dict[str, Any]]:
    """Filter rows where Industry column matches the query."""
    if not industry:
        return rows
    return [row for row in rows if _industry_matches(industry, row.get("Industry", ""))]


def platform_chooser(
    industry: str = "",
    region: str = "US",
    include_audience: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """Load platform benchmarks for the given industry and region.

    Args:
        industry: Industry keywords (e.g. "Health & Fitness", "E-commerce").
        region: "US" or "Global". Default "US".
        include_audience: Whether to include audience behavior data. Default True.

    Returns:
        Dict with platform performance data (CPC/CPM/CPA, CTR, conversion) and
        optional audience behavior (age, mobile usage, intent).
    """
    benchmarks_dir = getattr(agent_config, "BENCHMARKS_DIR", None)
    if benchmarks_dir is None:
        benchmarks_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "benchmarks"
    benchmarks_dir = Path(benchmarks_dir)
    if not benchmarks_dir.exists():
        return {
            "status": "error",
            "message": "Benchmarks directory not found.",
            "platforms": [],
            "audience": [],
        }

    region_upper = str(region).strip().upper() if region else "US"
    if region_upper not in ("US", "GLOBAL"):
        region_upper = "US"
    use_global = region_upper == "GLOBAL"

    platforms: list[dict[str, Any]] = []
    audience: list[dict[str, Any]] = []

    # Meta by industry
    meta_path = benchmarks_dir / "Meta_2024Q3_By_Industry.csv"
    meta_rows = _load_csv(meta_path)
    if meta_rows and industry:
        meta_rows = _filter_by_industry(meta_rows, industry)
    if meta_rows:
        for row in meta_rows:
            platforms.append({
                "platform": row.get("Platform", "Meta Ads"),
                "industry": row.get("Industry", ""),
                "region": row.get("Region", ""),
                "avg_cpc_usd": row.get("Avg_CPC_USD", ""),
                "avg_cpm_usd": row.get("Avg_CPM_USD", ""),
                "avg_cpa_usd": row.get("Avg_CPA_USD", ""),
                "avg_ctr_pct": row.get("Avg_CTR_%", ""),
                "avg_conversion_rate_pct": row.get("Avg_Conversion_Rate_%", ""),
            })

    # Google by industry
    google_path = benchmarks_dir / "Google_Ads_2025_By_Industry.csv"
    google_rows = _load_csv(google_path)
    if google_rows:
        if industry:
            google_rows = _filter_by_industry(google_rows, industry)
        # Google file is US-only; include if region is US or if no region filter
        if not use_global and google_rows:
            for row in google_rows:
                platforms.append({
                    "platform": row.get("Platform", "Google Ads"),
                    "industry": row.get("Industry", ""),
                    "region": row.get("Region", ""),
                    "avg_cpc_usd": row.get("Avg_CPC_USD", ""),
                    "avg_cpm_usd": row.get("Avg_CPM_USD", ""),
                    "avg_cpa_usd": row.get("Avg_CPA_USD", ""),
                    "avg_ctr_pct": row.get("Avg_CTR_%", ""),
                    "avg_conversion_rate_pct": row.get("Avg_Conversion_Rate_%", ""),
                })
    elif use_global:
        # Google file is US-only, no global Google by industry
        pass

    # CPC/CPM/CPA cross-platform (US or Global) - augment with platforms not yet covered
    cpc_filename = "CPC_CPM_CPA_US_Only.csv" if not use_global else "CPC_CPM_CPA_Global_Average.csv"
    cpc_path = benchmarks_dir / cpc_filename
    cpc_rows = _load_csv(cpc_path)
    if cpc_rows:
        platform_names = {p.get("platform", "").lower() for p in platforms}
        for row in cpc_rows:
            pname = (row.get("Platform") or "").strip()
            if not pname:
                continue
            # Include if no industry-specific data, or if platform not yet in list
            include = not platforms or pname.lower() not in platform_names
            if industry and platforms:
                # When we have industry matches, optionally filter CPC by industry
                cpc_ind = row.get("Industry", "").lower()
                if cpc_ind and _industry_matches(industry, row.get("Industry", "")):
                    include = True
            if include:
                platforms.append({
                    "platform": pname,
                    "industry": row.get("Industry", "General"),
                    "region": row.get("Region", ""),
                    "avg_cpc_usd": row.get("Avg_CPC_USD", ""),
                    "avg_cpm_usd": row.get("Avg_CPM_USD", ""),
                    "avg_cpa_usd": row.get("Avg_CPA_USD", ""),
                    "avg_ctr_pct": row.get("Avg_CTR_%", ""),
                    "avg_conversion_rate_pct": row.get("Avg_Conversion_Rate_%", ""),
                    "funnel_stage": row.get("Funnel_Stage", ""),
                })
                platform_names.add(pname.lower())

    # Audience behavior
    if include_audience:
        aud_filename = "Audience_Behavior_US_Only.csv" if not use_global else "Audience_Behavior_Global_Average.csv"
        aud_path = benchmarks_dir / aud_filename
        aud_rows = _load_csv(aud_path)
        for row in aud_rows:
            audience.append({
                "platform": row.get("Platform", ""),
                "region": row.get("Region", ""),
                "age_18_24_pct": row.get("Age_18_24_%", ""),
                "age_25_34_pct": row.get("Age_25_34_%", ""),
                "age_35_44_pct": row.get("Age_35_44_%", ""),
                "mobile_usage_pct": row.get("Mobile_Usage_%", ""),
                "primary_intent": row.get("Primary_Intent", ""),
                "purchase_intent_level": row.get("Purchase_Intent_Level", ""),
                "typical_funnel_role": row.get("Typical_Funnel_Role", ""),
            })

    return {
        "status": "ok",
        "message": f"Retrieved platform benchmarks for industry '{industry}' in region {region_upper}.",
        "industry_query": industry,
        "region": region_upper,
        "platforms": platforms,
        "audience": audience,
    }
