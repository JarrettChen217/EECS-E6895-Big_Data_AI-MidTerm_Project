#!/usr/bin/env bash
# Build frontend and run Flask (single process: UI + API).
# Usage (from repo root):  bash scripts/build_and_run.sh
# Then open http://localhost:9999 (or VITE_BACKEND_PORT from .env)

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Build frontend
if [[ ! -d "$REPO_ROOT/frontend/node_modules" ]]; then
  echo "Installing frontend deps..."
  (cd frontend && npm ci)
fi
echo "Building frontend..."
(cd frontend && npm run build)

# Activate venv
if [[ -z "$VIRTUAL_ENV" ]]; then
  if [[ -n "$VENV_PATH" ]]; then
    source "$VENV_PATH/bin/activate"
  elif [[ -d "$REPO_ROOT/.venv" ]]; then
    source "$REPO_ROOT/.venv/bin/activate"
  else
    echo "No venv found. Create .venv and install deps first."
    exit 1
  fi
fi

export PYTHONPATH=.:src
echo "Starting Flask (frontend + API)..."
exec python -m api.app
