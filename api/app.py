"""Flask API: GET /health, POST /agent, POST /api/advice-chat."""

import sys
import time
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


@app.route("/api/advice-chat", methods=["POST"])
def advice_chat():
    """Body: { messages: [{role, content}, ...] }. Returns { reply: str } or { reply, assign_time_ms }."""
    data = request.get_json() or {}
    messages = data.get("messages")
    if not messages or not isinstance(messages, list):
        return jsonify({"error": "Missing or invalid 'messages' (must be a list of {role, content})"}), 400
    # Normalize to list of {role, content}
    normalized = []
    for m in messages:
        if isinstance(m, dict) and "role" in m and "content" in m:
            normalized.append({"role": str(m["role"]), "content": str(m["content"])})
    if not normalized:
        return jsonify({"error": "No valid messages (each must have role and content)"}), 400
    try:
        from marketing_agent.llm import get_llm
        t0 = time.perf_counter()
        llm = get_llm()
        reply = llm.generate(normalized, max_new_tokens=512, temperature=0.7)
        assign_time_ms = round((time.perf_counter() - t0) * 1000)
        return jsonify({"reply": reply, "assign_time_ms": assign_time_ms})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
