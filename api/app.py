"""Flask API: GET /health, POST /agent."""

import sys
from pathlib import Path

# Ensure project root and src are on path (for prompts + marketing_agent)
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
if str(_root / "src") not in sys.path:
    sys.path.insert(0, str(_root / "src"))

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/agent", methods=["POST"])
def agent():
    """Body: {"question": "..."}. Returns run_agent result as JSON."""
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Missing or empty 'question'"}), 400
    try:
        from marketing_agent.agent.run import run_agent
        result = run_agent(question)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
