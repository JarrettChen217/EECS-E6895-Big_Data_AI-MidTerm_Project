# Marketing Advertiser AI Agent

Midterm project for **EECS E6895: Big Data AI** (Spring 2026).

**Authors:** Tianrui Fang (tf2639), Hao Chen (hc3625), Tianyu Zhan (tz2704) — Columbia University.

An AI advertising agent that helps new marketplace sellers with platform selection, budget allocation, ad format suggestions, and policy compliance. It uses a **Router → Tool Executor → Synthesizer** pipeline: the Router plans which tools to call, the Executor runs `platform_chooser` (benchmark data) and RAG (policy corpus), and the Synthesizer merges results into a final answer with citations.

---

## Repository structure

```
├── prompts/              # Prompt templates (router, RAG, synthesis)
├── src/marketing_agent/  # Agent core
│   ├── config.py         # Env-based config
│   ├── llm/              # LLM backend (HuggingFace / OpenAI)
│   ├── rag/              # RAG pipeline (corpus, retriever, FAISS)
│   ├── tools/            # platform_chooser, RAG tool
│   └── agent/            # Router, synthesizer, run_agent
├── api/app.py            # Flask API
├── frontend/             # React + Vite chat UI
├── data/
│   ├── benchmarks/       # CPC/CPM/CPA CSV data
│   └── corpus/           # Policy JSONL corpus
└── tests/
```

---

## How to install dependencies

### 1. Clone and enter the repo

```bash
git clone https://github.com/JarrettChen217/EECS-E6895-Big_Data_AI-MidTerm_Project.git
cd EECS-E6895-Big_Data_AI-MidTerm_Project
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install Python dependencies

First install project dependencies **without** PyTorch (to avoid version conflicts):

```bash
pip install -r requirements-no-torch.txt
```

Then install **PyTorch** according to your machine (choose one):

- **CPU only:**  
`pip install torch`
- **GPU (CUDA):**  
See [pytorch.org](https://pytorch.org/get-started/locally/) for the correct `pip install torch ...` command for your CUDA version.

### 4. Create and configure `.env` (required)

**You must create a `.env` file before running the project;** the application reads LLM keys and paths from it and will not start without it.

1. **Copy the example file:**
  ```bash
   cp .env.example .env
  ```
2. **Edit `.env` and set at least one LLM backend:**
  - **HuggingFace:** Set `LLM_BACKEND=huggingface`, then set `HF_TOKEN` to your HuggingFace token. Optionally set `HF_MODEL_NAME` (default: `Qwen/Qwen2.5-3B-Instruct`).
  - **OpenAI (or compatible API):** Set `LLM_BACKEND=openai`, then set `OPENAI_API_KEY`. For a custom base URL (e.g. Cherry), set `OPENAI_BASE_URL` and `OPENAI_MODEL` as needed.
3. **Proxy (Vite frontend <-> backend):**
  The Vite frontend proxies API requests to the Flask backend. Default is `http://localhost:9999`. If the port is in use, set `VITE_BACKEND_PORT` in `.env`; both the frontend dev server and the backend will then use that port to communicate.
4. **Optional:** `CORPUS_PATH` (default: `data/corpus/ad_policy_corpus.jsonl`), `EMBED_MODEL_NAME`, `RAG_TOP_K` — only change if you use a custom RAG corpus or embedding model.

---

## How to run the system

The repo includes a pre-built frontend in `frontend/dist`. **You only need to run the Flask backend**; it serves both the web UI and the API. No Node.js or separate frontend process is required.

All commands below assume you are in the **repository root**.

### 1. Activate the virtual environment

```bash
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Start the backend

```bash
PYTHONPATH=.:src python -m api.app
```

The app binds to port **9999** by default (or the value of `VITE_BACKEND_PORT` in `.env`). Open [http://localhost:9999](http://localhost:9999) in your browser to use the chat UI. Flask serves the frontend at `/` and the API at `/api/`*.

> To build and start in one go (requires Node.js): `bash scripts/build_and_run.sh`

---

### Optional: Running frontend and backend separately

For development with hot reload, you can run the Vite dev server and the Flask API as two processes. The frontend will proxy `/api` to the backend.

1. Activate the venv and start the backend (same as above):
  ```bash
   source .venv/bin/activate
   PYTHONPATH=.:src python -m api.app
  ```
2. In another terminal, install frontend deps and run the dev server (Node.js 18+):
  ```bash
   cd frontend
   npm ci
   npm run dev
  ```
3. Open the URL shown by Vite (e.g. [http://localhost:5173](http://localhost:5173)). The backend must be running for API calls to work.

---

### Run the agent in Python only (no UI)

To call the agent from the command line without starting the API or frontend:

```bash
source .venv/bin/activate
PYTHONPATH=.:src python -c "
from marketing_agent.agent.run import run_agent
result = run_agent('Which platforms should I use for a \$5k monthly ad budget?')
print(result['final_answer'])
"
```

---

## Example usage

With the **backend** running (Step 2 above), call the API (replace `9999` with your `PORT` if set):

```bash
curl http://localhost:9999/health
curl -X POST http://localhost:9999/agent -H "Content-Type: application/json" -d '{"question": "What are Meta ad policies for health claims?"}'
```

**Python-only** and **frontend chat** usage are described in **How to run the system** above.

---

## Tests

```bash
PYTHONPATH=.:src python -m pytest tests/ -v
```

---

## Config summary

Main variables read from `.env` (see `.env.example` for full list and defaults):


| Variable            | Purpose                                                                 |
| ------------------- | ----------------------------------------------------------------------- |
| `LLM_BACKEND`       | `huggingface` or `openai`                                               |
| `HF_TOKEN`          | HuggingFace API token (required when using HuggingFace)                 |
| `HF_MODEL_NAME`     | HuggingFace model name (e.g. `Qwen/Qwen2.5-3B-Instruct`)                |
| `OPENAI_API_KEY`    | OpenAI API key (required when using OpenAI)                             |
| `OPENAI_MODEL`      | OpenAI model name                                                       |
| `OPENAI_BASE_URL`   | Optional; for OpenAI-compatible APIs (e.g. Cherry)                      |
| `CORPUS_PATH`       | RAG corpus JSONL path (`doc_id`, `text` per line)                       |
| `EMBED_MODEL_NAME`  | Embedding model for RAG (e.g. `sentence-transformers/all-MiniLM-L6-v2`) |
| `RAG_TOP_K`         | Number of passages to retrieve                                          |
| `VITE_BACKEND_PORT` | Backend port for frontend proxy (e.g. `9999`)                           |


