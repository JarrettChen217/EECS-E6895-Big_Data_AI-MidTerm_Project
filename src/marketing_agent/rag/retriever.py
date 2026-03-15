"""FAISS vector store and retriever."""

from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    print("[warning]: langchain_huggingface not found, using langchain_community.HuggingFaceEmbeddings.")
    from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore


def get_embeddings(model_name: str) -> Embeddings:
    """Return HuggingFace Embeddings instance. Uses HF_TOKEN from config when set."""
    from marketing_agent import config as agent_config

    model_kwargs = {}
    if getattr(agent_config, "HF_TOKEN", ""):
        model_kwargs["token"] = agent_config.HF_TOKEN
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs if model_kwargs else None,
    )


def build_vectorstore(
    documents: list[Document],
    embed_model_name: Optional[str] = None,
    embeddings: Optional[Embeddings] = None,
) -> FAISS:
    """Build FAISS index from documents using config-driven or provided embeddings."""
    if embeddings is None:
        from marketing_agent import config as agent_config

        embeddings = get_embeddings(
            model_name=embed_model_name or agent_config.EMBED_MODEL_NAME,
        )
    return FAISS.from_documents(documents=documents, embedding=embeddings)


def get_retriever(
    vectorstore: FAISS,
    k: int = 3,
):
    """Return a retriever that returns top-k chunks."""
    return vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve(retriever, query: str) -> List[Document]:
    """Return top-k relevant chunks for the query (k set when building retriever)."""
    return retriever.invoke(query)
