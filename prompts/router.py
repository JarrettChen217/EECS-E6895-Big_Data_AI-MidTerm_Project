"""Router prompt: extract args and return plan [platform_chooser, rag x N]."""

# Tool names
TOOL_PLATFORM_CHOOSER = "platform_chooser"
TOOL_RAG = "rag"

# Max RAG steps to allow (caps duplicate/similar requests)
MAX_RAG_STEPS = 5

ROUTER_SYSTEM = "Output strictly valid JSON only. No extra text."

ROUTER_USER_TEMPLATE = """
You are a tool router for a Marketing Advertiser AI agent.

Return a plan with:
1) One platform_chooser step - with industry (inferred from product type) and region (default US)
2) Multiple rag steps (2 to 5) - each with a DIFFERENT policy question to gather comprehensive information

Each rag step should cover a distinct aspect, for example:
- Meta ads policy for <industry>
- Google Ads policy and restricted categories for <industry>
- TikTok ads policy and brand safety
- Ad compliance and prohibited claims for <topic>
- CPC/CPM benchmarks by platform

Return ONLY valid JSON with this schema:
{{
  "plan": [
    {{"tool": "platform_chooser", "args": {{"industry": "<extracted>", "region": "US", "include_audience": true}}}},
    {{"tool": "rag", "args": {{"question": "<aspect 1 policy query>", "k": 3}}}},
    {{"tool": "rag", "args": {{"question": "<aspect 2 policy query>", "k": 3}}}},
    ...
  ]
}}

Rules:
- Extract or infer "industry" from the user question (e.g. fitness app -> "Health & Fitness", e-commerce -> "E-commerce").
- Use 2 to 5 rag steps, each with a different question covering: Meta, Google, TikTok, compliance, or benchmarks.
- Do NOT repeat the same question. Each rag step must query a different aspect.
- region: use "US" unless user specifies a different region.
- k: 3 for each rag step.

User question:
{question}

JSON:
"""


def make_router_prompt(question: str) -> str:
    """Build the router user prompt with the given question."""
    return ROUTER_USER_TEMPLATE.format(question=question.strip()).strip()
