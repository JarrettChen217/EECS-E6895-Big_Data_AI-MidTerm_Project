#!/usr/bin/env bash
# Create venv and install dependencies (GPU: PyTorch with CUDA).
# Usage: from repo root, run:  bash scripts/setup_venv.sh
# Then:  source .venv/bin/activate

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Python 3.10+ recommended for CUDA 12.x
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" &>/dev/null; then
  PYTHON=python
fi

echo "Using: $PYTHON = $($PYTHON --version 2>&1)"
echo "Repo root: $REPO_ROOT"

# Create venv if missing
if [[ ! -d .venv ]]; then
  "$PYTHON" -m venv .venv
  echo "Created .venv"
fi

# Activate (this script may be sourced for interactive use)
# When run non-interactively we still need to install into .venv
.venv/bin/pip install -U pip

# Install PyTorch with CUDA first (so requirements.txt does not pull CPU-only torch)
# cu124 = CUDA 12.4 (works with 12.x and often forward-compatible with newer driver/CUDA 13)
# If you need cu121: use --index-url https://download.pytorch.org/whl/cu121
echo "Installing PyTorch with CUDA 12.4..."
.venv/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# Rest of dependencies (transformers, langchain, etc.)
echo "Installing project requirements..."
.venv/bin/pip install -r requirements.txt

# Optional: verify GPU visible to Python
echo ""
echo "Checking GPU availability in Python..."
.venv/bin/python -c "
import torch
print('PyTorch:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('Device:', torch.cuda.get_device_name(0))
    print('CUDA version (driver):', torch.version.cuda)
"

echo ""
echo "Done. Activate with:  source $REPO_ROOT/.venv/bin/activate"
echo "Then set .env (copy from .env.example) and run: PYTHONPATH=.:src python scripts/run_agent_cli.py \"Your question\""
