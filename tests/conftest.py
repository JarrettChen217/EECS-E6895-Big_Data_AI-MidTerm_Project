"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent

# Load .env before any tests run
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env", override=True)
except ImportError:
    pass

# Ensure project root and src are on path
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
if str(_root / "src") not in sys.path:
    sys.path.insert(0, str(_root / "src"))
