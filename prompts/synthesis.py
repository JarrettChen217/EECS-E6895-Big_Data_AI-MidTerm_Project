"""Synthesis prompt: system message for merging tool outputs into final answer."""

# Base system prompt (no citations yet)
SYNTHESIS_SYSTEM_BASE = (
    "You are a helpful advertising assistant.\n"
    "Use ONLY the provided tool outputs.\n"
    "Do NOT invent numbers or facts; use only values from the tool results.\n"
    "{citation_rule}"
    "Be concise and directly answer the question.\n"
)

# When RAG was used, we inject this into {citation_rule}
CITATION_RULE_TEMPLATE = (
    "Available citations: {citations}\n"
    "If you use any information from RAG/documentation, you MUST include citations like [doc_id].\n"
    "Your final answer MUST include at least one citation if citations are available.\n"
)


def get_synthesis_system(citations: list[str] | None = None) -> str:
    """Build the synthesis system message, optionally with citation rules."""
    if citations:
        citation_rule = CITATION_RULE_TEMPLATE.format(
            citations=", ".join(f"[{c}]" for c in citations)
        )
    else:
        citation_rule = ""
    return SYNTHESIS_SYSTEM_BASE.format(citation_rule=citation_rule)
