"""Run agent: route -> run_plan -> synthesize."""

from __future__ import annotations

from typing import Any

from marketing_agent import config as agent_config
from marketing_agent.llm import get_llm
from marketing_agent.llm.base import BaseLLM
from marketing_agent.rag import load_jsonl_corpus, build_vectorstore, get_retriever
from marketing_agent.tools import run_plan, make_tool_rag, ad_planner, compliance_check, get_campaign
from marketing_agent.agent.router import route_question
from marketing_agent.agent.synthesizer import synthesize_answer

# Lazy singletons for retriever (avoid reload on every call). LLM is singleton in llm.get_llm().
_retriever = None
_tool_registry: dict[str, Any] | None = None


def _get_default_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever
    if agent_config.CORPUS_PATH and agent_config.CORPUS_PATH.exists():
        docs = load_jsonl_corpus(agent_config.CORPUS_PATH)
        vs = build_vectorstore(docs, embed_model_name=agent_config.EMBED_MODEL_NAME)
        _retriever = get_retriever(vs, k=agent_config.RAG_TOP_K)
    return _retriever


def _build_tool_registry(llm: BaseLLM, retriever) -> dict[str, Any]:
    reg = {
        "ad_planner": ad_planner,
        "compliance_check": compliance_check,
        "get_campaign": get_campaign,
    }
    if retriever is not None:
        reg["rag"] = make_tool_rag(retriever, llm)
    return reg


def run_agent(
    question: str,
    llm: BaseLLM | None = None,
    retriever=None,
) -> dict[str, Any]:
    """Run the full agent: route -> execute tools -> synthesize answer."""
    llm = llm or get_llm()
    if retriever is None:
        retriever = _get_default_retriever()
    tool_registry = _build_tool_registry(llm, retriever)

    plan = route_question(question, llm)
    trace = run_plan(plan, tool_registry)

    # When only get_campaign was used and it returned a campaign with image, skip LLM synthesizer
    # and use a fixed short reply so we never get long ad copy or clarifying questions.
    plan_steps = plan.get("plan") or []
    if len(plan_steps) == 1 and plan_steps[0].get("tool") == "get_campaign":
        for t in trace:
            if t.get("tool") == "get_campaign" and isinstance(t.get("result"), dict):
                res = t["result"]
                if res.get("status") == "ok" and res.get("campaign", {}).get("image_url"):
                    camp_name = (res.get("campaign") or {}).get("name") or "campaign"
                    final_answer = f"Here is the {camp_name} creative from our campaign library."
                    return {
                        "question": question,
                        "plan": plan_steps,
                        "trace": trace,
                        "final_answer": final_answer,
                    }

    final_answer = synthesize_answer(question, trace, llm)

    return {
        "question": question,
        "plan": plan.get("plan", []),
        "trace": trace,
        "final_answer": final_answer,
    }
