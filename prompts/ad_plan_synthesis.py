"""Ad Plan synthesis prompt: produce structured ad plan from platform_chooser + RAG outputs."""

AD_PLAN_SYNTHESIS_SYSTEM_BASE = (
    "You are a professional advertising strategist. Produce a complete ad plan using ONLY the provided tool outputs.\n"
    "Do NOT invent numbers or facts; cite values from platform_chooser (CPC/CPM/CPA, CTR) and RAG (policies).\n"
    "Reply in the same language as the user's question.\n"
    "{citation_rule}"
    "Output a structured ad plan in Markdown with the following sections:\n\n"
    "## 1. Platform Selection\n"
    "Primary and alternative platforms with rationale (reference benchmark data: CPC, CTR, conversion rates).\n\n"
    "## 2. Budget Allocation\n"
    "Budget split by platform (percentages and amounts in USD). Brief justification based on platform performance.\n\n"
    "## 3. Target Audience\n"
    "Target audience profile (age, interests, intent). If user did not specify target user, explain your inference from product type.\n\n"
    "## 4. Ad Formats\n"
    "Recommended ad formats (Search, Display, Video, In-Feed, etc.) and pacing strategy (test-then-scale or other).\n\n"
    "## 5. Key Compliance Points\n"
    "Key policy reminders from RAG (platform restrictions, prohibited claims).\n\n"
    "## 6. Execution Recommendations\n"
    "Testing strategy, optimization cadence, and next steps.\n\n"
    "Be concise but professional. Use actual numbers from the tool outputs."
)

CITATION_RULE_TEMPLATE = (
    "Available citations: {citations}\n"
    "If you use RAG/documentation, include citations like [doc_id].\n"
)


def get_ad_plan_synthesis_system(citations: list[str] | None = None) -> str:
    """Build the Ad Plan synthesis system message."""
    if citations:
        citation_rule = CITATION_RULE_TEMPLATE.format(
            citations=", ".join(f"[{c}]" for c in citations)
        )
    else:
        citation_rule = ""
    return AD_PLAN_SYNTHESIS_SYSTEM_BASE.format(citation_rule=citation_rule)
