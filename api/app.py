"""Flask API: GET /health, POST /agent, POST /api/advice-chat."""

import os
import sys
import time
from pathlib import Path
import subprocess

# Ensure project root and src are on path (for prompts + marketing_agent)
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
if str(_root / "src") not in sys.path:
    sys.path.insert(0, str(_root / "src"))

import json
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

# Campaigns DB path (same as marketing_agent config)
_CAMPAIGNS_JSON = _root / "data" / "campaigns.json"
_CAMPAIGNS_DIR = _root / "data" / "campaigns"


def _load_campaign_by_id(campaign_id):
    """Load campaign record by id from data/campaigns.json."""
    if not _CAMPAIGNS_JSON.exists():
        return None
    try:
        with open(_CAMPAIGNS_JSON, "r", encoding="utf-8") as f:
            campaigns = json.load(f)
        for c in campaigns:
            if c.get("id") == campaign_id:
                return c
    except Exception:
        pass
    return None


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


@app.route("/api/agent", methods=["POST"])
def api_agent():
    """Unified Agent endpoint for frontend.

    Body: {"question": "...", "messages": [{role, content}, ...]?}
    Returns: {"reply": str, "raw": {...}} where raw is the full run_agent dict.
    """
    data = request.get_json() or {}
    question = str(data.get("question", "")).strip()
    if not question:
        return jsonify({"error": "Missing or empty 'question'"}), 400

    # Optional: normalize messages for future use / logging (currently unused by run_agent)
    messages = data.get("messages")
    normalized_messages = None
    if isinstance(messages, list):
        tmp = []
        for m in messages:
            if isinstance(m, dict) and "role" in m and "content" in m:
                tmp.append({"role": str(m["role"]), "content": str(m["content"])})
        if tmp:
            normalized_messages = tmp

    try:
        from marketing_agent.agent.run import run_agent

        # Currently run_agent only accepts question; messages are kept for future extensions.
        result = run_agent(question)
        reply = result.get("final_answer") or ""
        return jsonify({"reply": reply, "raw": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/campaigns/<campaign_id>/image", methods=["GET"])
def campaign_image(campaign_id):
    """Serve campaign creative image by campaign id."""
    campaign = _load_campaign_by_id(campaign_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404
    image_path = campaign.get("image_path")
    if not image_path:
        return jsonify({"error": "No image for this campaign"}), 404
    file_path = _CAMPAIGNS_DIR / image_path
    if not file_path.is_file():
        return jsonify({"error": "Image file not found"}), 404
    return send_file(file_path, mimetype="image/jpeg")


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
    PORT = 9999
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

    vite_env = {**os.environ, "VITE_BACKEND_PORT": str(PORT)}
    vite_proc = subprocess.Popen(["npm", "run", "dev"], cwd=str(frontend_dir), env=vite_env)

    print(f"Starting Flask API on port {PORT}")
    try:
        app.run(host="0.0.0.0", port=PORT)
    finally:
        vite_proc.terminate()
        print("Vite process terminated")
