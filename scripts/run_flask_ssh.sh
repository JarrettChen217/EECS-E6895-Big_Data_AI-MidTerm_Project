#!/usr/bin/env bash
# Start Flask API on SSH (activates venv, sets PYTHONPATH, runs api.app on 0.0.0.0:5000).
# Usage (from anywhere):  bash scripts/run_flask_ssh.sh
# Then:  curl http://localhost:5000/health
#        curl -X POST http://localhost:5000/agent -H "Content-Type: application/json" -d '{"question": "..."}'

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Activate venv if not already
if [[ -z "$VIRTUAL_ENV" ]]; then
  if [[ -n "$VENV_PATH" ]]; then
    source "$VENV_PATH/bin/activate"
  elif [[ -d "$REPO_ROOT/.venv" ]]; then
    source "$REPO_ROOT/.venv/bin/activate"
  elif [[ -d "$HOME/python-envs/normwear_env" ]]; then
    source "$HOME/python-envs/normwear_env/bin/activate"
  else
    echo "No venv found. Set VENV_PATH or create .venv in repo root."
    exit 1
  fi
fi

export PYTHONPATH=.:src
exec python -m api.app
