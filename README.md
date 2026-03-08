# Marketing Advertiser AI Agent

Midterm project of EECS-E6895 Big Data AI (2026 Spring).

AI advertising agent for new marketplace sellers: platform/ad format recommendations, budget allocation and pacing, ad design plans, and compliance/risk checks. Data sources include ad policies (Meta, Google, TikTok, Amazon) and CPC/CPM/CPA benchmarks.

## Architecture

- **Router**: Intent classification → JSON plan (which tools to call).
- **Tools**: `platform_chooser` (benchmarks from data/benchmarks), RAG (policy/docs from corpus).
- **Synthesizer**: Merges tool results into a final answer with citations.

Flow: User question → Router → `run_plan` (tools) → Synthesizer → Final answer.

## Project layout

```
├── prompts/           # Centralized prompts (router, RAG, synthesis)
├── src/marketing_agent/
│   ├── config.py      # Env-based config
│   ├── llm/           # LLM abstraction (HuggingFace, OpenAI)
│   ├── rag/           # RAG pipeline (corpus, retriever, pipeline)
│   ├── tools/         # Tool registry, platform_chooser, RAG tool
│   ├── agent/         # Router, synthesizer, run_agent
│   └── chat.py        # Multi-turn chat (optional)
├── api/app.py         # Flask: GET /health, POST /agent, POST /api/advice-chat
├── frontend/          # Vite + React chat UI (Ad Advice Chat)
├── data/corpus/       # JSONL corpus (doc_id, text)
└── tests/
```

## Setup

### Option A: GPU (Ubuntu + NVIDIA + CUDA)

One-shot venv + PyTorch (CUDA 12.4) + project deps:

```bash
bash scripts/setup_venv.sh
source .venv/bin/activate
```

See [docs/ENV_SETUP.md](docs/ENV_SETUP.md) for venv, GPU, and CUDA compatibility.

### Option B: Local / CPU

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Env and secrets

1. Copy env and set secrets:

   ```bash
   cp .env.example .env
   # Edit .env: set HF_TOKEN (and optionally OPENAI_API_KEY, CORPUS_PATH, etc.)
   ```

2. An example RAG corpus is at `data/corpus/ad_policy_corpus.jsonl` (Meta/Google/TikTok policy snippets). For your own data, use the same JSONL format: each line is a JSON object with at least `doc_id` and `text`.

## Usage

### Python

Run from repo root with `PYTHONPATH` so that `marketing_agent` and `prompts` resolve:

```bash
PYTHONPATH=.:src python -c "
from marketing_agent.agent.run import run_agent
result = run_agent('Which platforms should I use for a \$5k monthly ad budget?')
print(result['final_answer'])
"
```

Or use the CLI script (same PYTHONPATH):

```bash
PYTHONPATH=.:src python scripts/run_agent_cli.py "What are Meta's ad policies for health?"
```

**On SSH:** You can use the runner scripts (no need to set PYTHONPATH or activate venv manually): `bash scripts/run_agent_ssh.sh "question"` and `bash scripts/run_flask_ssh.sh` for the API. See [docs/ENV_SETUP.md](docs/ENV_SETUP.md) section 6.

### Backend (Flask API)

Start the server from **repo root** so `api` and `src` are on path (default port **5000**):

```bash
PYTHONPATH=.:src python -m api.app
# or: FLASK_APP=api.app:app PYTHONPATH=.:src flask run
```

Then:

```bash
# Health
curl http://localhost:5000/health

# Agent
curl -X POST http://localhost:5000/agent -H "Content-Type: application/json" -d '{"question": "What are Meta ad policies for health claims?"}'

# Chat (advice-chat, used by frontend)
curl -X POST http://localhost:5000/api/advice-chat -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"Hello"}]}'

# Unified Agent for frontend
curl -X POST http://localhost:5000/api/agent -H "Content-Type: application/json" -d '{"question": "What platforms should I use for a 5k budget?", "messages":[{"role":"user","content":"I am a new seller"}]}'
```

The chat endpoint returns `{ "reply": "...", "assign_time_ms": ... }`. OpenAI API key is read from `.env` on the server only (never exposed to the frontend).

### Frontend (Chat UI)

React chat page (Vite) with Columbia background. From repo root:

```bash
cd frontend
npm install
npm run dev
```

Then open the URL shown (e.g. http://localhost:5173). The dev server proxies `/api` to the backend at http://localhost:5000, so the backend must be running for chat to work.

- **Background**: `frontend/public/Columbia.jpg` is used as the full-page background (with overlay for readability). If you have the image at `frontend/Columbia.jpg`, copy it to `frontend/public/Columbia.jpg`.
- **Send**: Enter to send, Shift+Enter for new line; or use the Send button.

## Tests

Run tests (requires project dependencies: `pip install -r requirements.txt`):

```bash
PYTHONPATH=.:src python -m pytest tests/ -v
```

## Config

See `.env.example`. Main variables:

- `LLM_BACKEND`: `huggingface` (default) or `openai`
- `HF_TOKEN`, `HF_MODEL_NAME`: for HuggingFace
- `OPENAI_API_KEY`, `OPENAI_MODEL`: for OpenAI
- `CORPUS_PATH`, `EMBED_MODEL_NAME`, `RAG_TOP_K`: RAG behavior

## References

- Proposal: `Marketing _ Advertiser 1.pdf`
- Agent structure refactored from: `Final Submission.ipynb` (HW1)
