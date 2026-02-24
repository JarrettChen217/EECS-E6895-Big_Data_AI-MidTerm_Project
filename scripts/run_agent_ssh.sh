#!/usr/bin/env bash
# Run Marketing Advertiser Agent CLI on SSH (activates venv, sets PYTHONPATH, runs agent).
# Usage (from anywhere):  bash scripts/run_agent_ssh.sh "Your question here"
# Or from repo root:     ./scripts/run_agent_ssh.sh "What are Meta's ad policies for health?"

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
exec python scripts/run_agent_cli.py "$@"
