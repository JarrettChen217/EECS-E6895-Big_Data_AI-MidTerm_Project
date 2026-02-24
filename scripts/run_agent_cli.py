#!/usr/bin/env python3
"""CLI to run the Marketing Advertiser agent (for E2E verification).

Usage (from repo root):
  PYTHONPATH=.:src python scripts/run_agent_cli.py "What are Meta's ad policies for health?"
  PYTHONPATH=.:src python scripts/run_agent_cli.py "Which platforms should I use for a $5k monthly budget?"
"""

import sys
from pathlib import Path

# Add repo root and src so marketing_agent and prompts resolve
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "src"))

from marketing_agent.agent.run import run_agent


def main():
    question = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else None
    if not question:
        question = "What are Meta's ad policies for health claims?"
        print(f"No question provided; using: {question}\n")
    print("Question:", question)
    print()
    result = run_agent(question)
    print("Plan:", result["plan"])
    print()
    print("Final answer:")
    print(result["final_answer"])


if __name__ == "__main__":
    main()
