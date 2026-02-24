"""Load JSONL corpus for RAG (doc_id, text per line)."""

import json
import os
from pathlib import Path

from langchain_core.documents import Document


def load_jsonl_corpus(path: str | Path) -> list[Document]:
    """Load a JSONL corpus where each line is one retrieval chunk.

    Required fields per line: doc_id, text.
    Any other fields are stored in Document.metadata.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Corpus file not found: {path}")

    docs: list[Document] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "doc_id" not in obj or "text" not in obj:
                raise ValueError(
                    f"Invalid JSONL at line {line_no}: missing doc_id or text."
                )
            text = obj["text"]
            metadata = {k: v for k, v in obj.items() if k != "text"}
            docs.append(Document(page_content=text, metadata=metadata))

    if not docs:
        raise ValueError("Corpus loaded 0 documents. Check your file path/content.")
    return docs
