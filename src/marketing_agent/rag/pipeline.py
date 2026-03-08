"""RAG pipeline: retrieve -> build messages -> generate answer with evidence."""

from __future__ import annotations

from typing import Any, List

from langchain_core.documents import Document

from marketing_agent.llm.base import BaseLLM

# Prompts at project root; import when running with PYTHONPATH including repo root
try:
    from prompts.rag_system import RAG_SYSTEM
except ImportError:
    print("[warning]: prompts.rag_system not found, using default RAG_SYSTEM.")
    RAG_SYSTEM = (
        "You are a retrieval-augmented assistant.\n"
        "Answer the user's question using ONLY the provided context.\n"
        "You MUST cite sources using doc_id in square brackets.\n"
    )


def build_rag_messages(context_docs: List[Document], question: str) -> List[dict[str, str]]:
    """Format retrieved chunks into messages with [doc_id] headers. Uses RAG_SYSTEM."""
    ctx_blocks = []
    for d in context_docs:
        doc_id = d.metadata.get("doc_id", "unknown")
        ctx_blocks.append(f"[{doc_id}]\n{d.page_content.strip()}")
    context = "\n\n".join(ctx_blocks)
    user = f"Context:\n{context}\n\nQuestion: {question}"
    return [
        {"role": "system", "content": RAG_SYSTEM},
        {"role": "user", "content": user},
    ]


def show_retrieval_evidence(
    query: str,
    retrieved_docs: List[Document],
    max_chars: int = 300,
) -> None:
    """Print retrieved doc_id and snippet (for grading/debug)."""
    print("=" * 90)
    print("RAG EVIDENCE (REQUIRED)")
    print("=" * 90)
    print(f"Query: {query}")
    print(f"Retrieved: {len(retrieved_docs)} chunks\n")
    for i, d in enumerate(retrieved_docs, 1):
        doc_id = d.metadata.get("doc_id", "N/A")
        dtype = d.metadata.get("type", "N/A")
        title = d.metadata.get("title", "")
        snippet = (
            d.page_content[:max_chars].strip()
            + ("..." if len(d.page_content) > max_chars else "")
        )
        print(f"[{i}] doc_id={doc_id} | type={dtype} | title={title}")
        print(f"Snippet: {snippet}\n")


def rag_answer(
    question: str,
    retriever,
    llm: BaseLLM,
    k: int = 3,
    show_evidence: bool = True,
    max_new_tokens: int = 256,
) -> dict[str, Any]:
    """End-to-end RAG: retrieve -> evidence (optional) -> build messages -> generate.

    Returns: {"answer": str, "evidence": [{"doc_id", "title", "var", "text"}, ...]}
    """
    docs = retriever.invoke(question)
    if show_evidence:
        show_retrieval_evidence(question, docs)

    messages = build_rag_messages(docs, question)
    answer = llm.generate(messages, max_new_tokens=max_new_tokens, temperature=0.0)

    evidence = [
        {
            "doc_id": d.metadata.get("doc_id", "N/A"),
            "title": d.metadata.get("title", "N/A"),
            "var": d.metadata.get("var", ""),
            "text": d.page_content,
        }
        for d in docs
    ]
    return {"answer": answer, "evidence": evidence}
