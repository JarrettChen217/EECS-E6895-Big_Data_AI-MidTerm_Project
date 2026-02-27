"""Load configuration from environment variables."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    load_dotenv(_PROJECT_ROOT / ".env")
except ImportError:
    pass
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# LLM
LLM_BACKEND = os.getenv("LLM_BACKEND", "huggingface")
HF_TOKEN = os.getenv("HF_TOKEN", "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")
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "Qwen/Qwen2.5-3B-Instruct")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# RAG: resolve path relative to project root
_CORPUS_PATH = os.getenv("CORPUS_PATH", "data/corpus/ad_policy_corpus.jsonl")
CORPUS_PATH = (_PROJECT_ROOT / _CORPUS_PATH) if _CORPUS_PATH else None
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
