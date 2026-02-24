"""RAG as a tool for the agent (question, k) -> {answer, evidence}."""

from typing import Any, Callable

from marketing_agent.llm.base import BaseLLM
from marketing_agent.rag.pipeline import rag_answer


def make_tool_rag(retriever, llm: BaseLLM) -> Callable[..., dict[str, Any]]:
    """Build tool_rag that uses the given retriever and LLM."""

    def tool_rag(question: str, k: int = 3, **kwargs: Any) -> dict[str, Any]:
        return rag_answer(
            question,
            retriever=retriever,
            llm=llm,
            k=k,
            show_evidence=True,
        )

    return tool_rag
