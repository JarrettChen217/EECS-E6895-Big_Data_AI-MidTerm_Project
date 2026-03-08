"""Router prompt: intent classification for Marketing Advertiser agent.

Output schema: {"plan": [{"tool": "...", "args": {...}}, ...]}
Available tools: platform_chooser, rag, ad_planner, compliance_check, get_campaign.
"""

# Tool names and arg schemas (for prompt text)
TOOL_PLATFORM_CHOOSER = "platform_chooser"
TOOL_RAG = "rag"
TOOL_AD_PLANNER = "ad_planner"
TOOL_COMPLIANCE_CHECK = "compliance_check"

ROUTER_TOOLS_DESCRIPTION = """
1) platform_chooser
   args: {"industry": string (product type/industry, e.g. "Health & Fitness", "E-commerce"), "region": string (optional, "US" or "Global", default "US"), "include_audience": boolean (optional, default true)}
   Use for: getting CPC/CPM/CPA benchmarks, CTR, conversion rates, and audience behavior by platform. Required for ad plan requests with product type + budget.

2) rag
   args: {"question": string, "k": integer (optional, default 3)}
   Use for: ad policies, platform rules, compliance documentation, policy constraints (Meta, Google, TikTok, etc.).

3) ad_planner
   args: {"keywords": string, "product_info": string (optional), "budget_total": number (optional), "objectives": string (optional)}
   Use for: legacy/fallback platform recommendations (prefer platform_chooser + synthesis for full ad plans).

4) compliance_check
   args: {"content": string (draft copy or plan to check)}
   Use for: validating draft copy or plan for policy violations, risks, banned claims.

5) get_campaign
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
- PRIORITY: If the user asks for an ad or creative for a specific industry/category (e.g. "Give me a healthcare ad", "I want a healthcare ad", "healthcare ad campaign", "healthcare creative"), use ONLY get_campaign with that category. Do NOT use platform_chooser, ad_planner or rag for this.
- AD PLAN PRIORITY: If the user wants a full ad plan with product type + budget (e.g. "I have $5000 for a fitness app", "Plan ads for e-commerce, $10k budget", "Budget $3k, target young adults for beauty products"), use platform_chooser (with industry inferred from product type) and rag (for policy info). Plan: [{{"tool": "platform_chooser", "args": {{"industry": "<inferred>"}}}}, {{"tool": "rag", "args": {{"question": "<platform> ads policy for <industry/topic>"}}}}]. Extract industry, budget, target user from the question.
- Use platform_chooser for: any request that needs platform benchmarks, CPC/CPM/CPA, audience behavior to make platform/budget decisions.
- Use rag for: policy questions, platform rules, compliance documentation (only when NOT asking for a specific industry ad creative).
- Use ad_planner for: simple strategy questions when platform_chooser is not needed (rare).
- Use compliance_check for: validating draft copy or plan for policy violations, risks.
- Use get_campaign for: any request for an ad/creative for an industry (healthcare, etc.). Returns a stored campaign with image.
- Choose the MINIMAL set of tools. For "healthcare ad" → get_campaign only. For "ad plan with $5k for fitness" → platform_chooser + rag.

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
