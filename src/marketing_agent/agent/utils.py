"""Agent utilities: JSON extraction from LLM output."""

import json


def extract_json(text: str) -> dict:
    """Extract first JSON object from text (handles markdown fences and extra text)."""
    if not text:
        raise ValueError("No JSON object found in the text (empty string).")

    # Try to find '{' and parse a JSON object starting from there.
    # This automatically handles surrounding text, markdown fences, and avoids regex corruption
    # which can destroy backticks inside pure JSON strings.
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No '{{' found in the text. Cannot extract JSON object. Text starts with: {text[:50]!r}")

    errors = []
    
    while start != -1:
        try:
            result, _ = json.JSONDecoder().raw_decode(text[start:])
            if isinstance(result, dict):
                print("--------------------------------")
                print("resultof extract_json")
                print(result)
                print("--------------------------------")
                return result
        except json.JSONDecodeError as e:
            errors.append(f"Parse error at index {start}: {e}")
            
        start = text.find("{", start + 1)

    error_msg = "\n  - ".join(errors)
    raise ValueError(f"Failed to extract JSON object from text. Attempts:\n  - {error_msg}\nOriginal text length: {len(text)}\nOriginal text snippet: {text[:200]!r}")
