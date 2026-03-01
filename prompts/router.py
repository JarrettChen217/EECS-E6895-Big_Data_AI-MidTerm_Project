"""Router prompt: intent classification for Marketing Advertiser agent.

Output schema: {"plan": [{"tool": "...", "args": {...}}, ...]}
Available tools: rag, ad_planner, compliance_check.
"""

# Tool names and arg schemas (for prompt text)
TOOL_RAG = "rag"
TOOL_AD_PLANNER = "ad_planner"
TOOL_COMPLIANCE_CHECK = "compliance_check"

ROUTER_TOOLS_DESCRIPTION = """
1) rag
   args: {"question": string, "k": integer (optional, default 3)}
   Use for: ad policies, platform rules, CPC/CPM/CPA benchmarks, documentation.

2) ad_planner
   args: {"keywords": string, "product_info": string (optional), "budget_total": number (optional), "objectives": string (optional)}
   Use for: platform recommendations, ad format suggestions, budget allocation, pacing.

3) compliance_check
   args: {"content": string (draft copy or plan to check)}
   Use for: checking draft against policies, patent/risk/compliance, banned claims.

4) get_campaign
   args: {"category": string (e.g. "healthcare"), "industry": string (optional, alias for category)}
   Use for: when user asks for an ad solution or creative for a specific industry/category (e.g. healthcare). Returns a stored campaign with creative image.
"""

ROUTER_SYSTEM = "Output strictly valid JSON only. No extra text."

ROUTER_USER_TEMPLATE = """
You are a tool router for a Marketing Advertiser AI agent.

Return ONLY valid JSON with this schema:
{{
  "plan": [
    {{"tool": "...", "args": {{...}}}},
    ...
  ]
}}

Available tools:
{tools_description}

Routing rules (follow strictly):
- Use rag for: policy questions, platform specs, benchmarks, definitions, documentation.
- Use ad_planner for: which platforms/formats to use, budget split, pacing, strategy.
- Use compliance_check for: validating draft copy or plan for policy violations, risks.
- Use get_campaign for: when user asks for an ad solution/creative for a specific industry or category (e.g. "healthcare", "I want a healthcare ad"). Prefer get_campaign with category/industry matching the request.
- Choose the MINIMAL set of tools.
- If both policy info and strategy are needed, include both rag and ad_planner.
- If user provides draft text to check, use compliance_check (and optionally rag).

User question:
{question}

JSON:
"""


def make_router_prompt(question: str) -> str:
    """Build the router user prompt with the given question."""
    return ROUTER_USER_TEMPLATE.format(
        tools_description=ROUTER_TOOLS_DESCRIPTION.strip(),
        question=question.strip(),
    ).strip()
