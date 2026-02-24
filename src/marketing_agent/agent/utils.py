"""Agent utilities: JSON extraction from LLM output."""

import json
import re


def extract_json(text: str) -> dict:
    """Extract first JSON object from text (handles markdown fences and extra text)."""
    text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()
    # Find outermost {...} for nested structures like {"plan": [...]}
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in the text.")
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError("No complete JSON object found in the text.")
