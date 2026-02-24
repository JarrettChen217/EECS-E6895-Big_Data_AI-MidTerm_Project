"""RAG pipeline: corpus, retriever, and answer generation."""

from marketing_agent.rag.corpus import load_jsonl_corpus
from marketing_agent.rag.retriever import build_vectorstore, get_retriever, retrieve
from marketing_agent.rag.pipeline import (
    build_rag_messages,
    rag_answer,
    show_retrieval_evidence,
)

__all__ = [
    "load_jsonl_corpus",
    "build_vectorstore",
    "get_retriever",
    "retrieve",
    "build_rag_messages",
    "rag_answer",
    "show_retrieval_evidence",
]
