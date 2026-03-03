"""Synthesizer: merge tool trace into final answer with citations."""

from __future__ import annotations

import json
import re
from typing import Any, List

from marketing_agent.llm.base import BaseLLM

try:
    from prompts.synthesis import get_synthesis_system
except ImportError:

    def get_synthesis_system(citations: list[str] | None = None) -> str:
        base = "You are a helpful assistant. Use ONLY the provided tool outputs. Be concise.\n"
        if citations:
            base += f"Available citations: {', '.join(f'[{c}]' for c in citations)}\n"
            base += "Include at least one citation when using RAG.\n"
        return base


def _collect_rag_citations(trace: List[dict[str, Any]]) -> list[str]:
    for t in trace:
        if t.get("tool") == "rag" and isinstance(t.get("result"), dict):
            ev = t["result"].get("evidence", [])
            doc_ids = []
            for item in ev:
                doc_id = item.get("doc_id")
                if doc_id and doc_id not in doc_ids:
                    doc_ids.append(doc_id)
            return doc_ids
    return []


def _has_citation(text: str) -> bool:
    return bool(re.search(r"\[[^\[\]]+\]", text))


def _get_campaign_succeeded(trace: List[dict[str, Any]]) -> bool:
    """True if get_campaign was used and returned a campaign with image."""
    for t in trace:
        if t.get("tool") == "get_campaign" and isinstance(t.get("result"), dict):
            res = t["result"]
            if res.get("status") == "ok" and res.get("campaign", {}).get("image_url"):
                return True
    return False


def synthesize_answer(
    question: str,
    trace: List[dict[str, Any]],
    llm: BaseLLM,
    max_new_tokens: int = 256,
) -> str:
    """Merge tool outputs into one answer; enforce citation if RAG was used."""
    citations = _collect_rag_citations(trace)
    tool_blocks = []
    for t in trace:
        tool_blocks.append(
            f"Tool: {t['tool']}\nArgs: {json.dumps(t['args'], ensure_ascii=False)}\n"
            f"Result: {json.dumps(t['result'], ensure_ascii=False)[:1500]}"
        )
    tool_text = "\n\n".join(tool_blocks)

    system = get_synthesis_system(citations)
    # When get_campaign returned a campaign with image, keep reply short so the image is the focus
    if _get_campaign_succeeded(trace):
        system += "\nThe user asked for a campaign creative. get_campaign returned a campaign with an image (shown below). Reply in 1-2 short sentences only, e.g. 'Here is the healthcare ad creative from our campaign library.' Do NOT write long ad copy, do NOT ask clarifying questions."
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Question: {question}\n\nTool outputs:\n{tool_text}\n\nWrite the final answer:"},
    ]
    answer = llm.generate(messages, max_new_tokens=max_new_tokens, temperature=0.2)

    if citations and not _has_citation(answer):
        answer = answer.strip() + f"\n\nSources: [{citations[0]}]"
    return answer
