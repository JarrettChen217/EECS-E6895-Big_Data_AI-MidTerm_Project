"""FAISS vector store and retriever."""

from pathlib import Path
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore


def build_vectorstore(
    documents: list[Document],
    embed_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> FAISS:
    """Build FAISS index from documents."""
    embeddings: Embeddings = HuggingFaceEmbeddings(model_name=embed_model_name)
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
