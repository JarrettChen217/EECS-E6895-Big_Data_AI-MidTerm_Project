#!/usr/bin/env python3
"""
Standalone test script: call Cherry Studio (OpenAI-compatible) API using the same
config as the backend. Use for debugging 401 invalid token etc.

Usage:
  1. In project root .env set (for Cherry Studio):
     OPENAI_API_KEY=sk-your-key-here
     OPENAI_BASE_URL=https://open.cherryin.net/v1
     OPENAI_MODEL=openai/gpt-5-chat
  2. From project root run: python scripts/test_cherry_openai.py
"""

import os
import sys
from pathlib import Path

# Load .env (same as config)
_root = Path(__file__).resolve().parent.parent
_dotenv = _root / ".env"
if _dotenv.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_dotenv, override=True)
    except ImportError:
        pass

API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()


def main():
    if not API_KEY:
        print("Error: OPENAI_API_KEY not set. Configure it in .env or export it.", file=sys.stderr)
        print("Example: OPENAI_API_KEY=sk-your-key-here", file=sys.stderr)
        sys.exit(1)

    print(f"BASE_URL: {BASE_URL}")
    print(f"MODEL:    {MODEL}")
    print(f"API_KEY:  {API_KEY[:8]}...{API_KEY[-4:] if len(API_KEY) > 12 else '***'}")
    print("-" * 50)

    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "Say hello in one sentence."}],
        )
        text = (response.choices[0].message.content or "").strip()
        print("Success! Reply:", text)
    except Exception as e:
        print("Request failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
