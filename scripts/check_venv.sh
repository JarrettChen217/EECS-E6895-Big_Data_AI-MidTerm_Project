#!/usr/bin/env bash
# 检查当前环境：是否在 venv 内、PyTorch 版本、CUDA 是否可用（不安装任何东西）
# Usage:  source .venv/bin/activate && bash scripts/check_venv.sh
#     or:  bash scripts/check_venv.sh   (会尝试用 .venv/bin/python)

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# 优先使用当前 shell 的 python（若已 activate venv），否则用 .venv 里的
if [[ -n "$VIRTUAL_ENV" ]]; then
  PYTHON="python"
  echo "Using venv: $VIRTUAL_ENV"
else
  if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
    PYTHON="$REPO_ROOT/.venv/bin/python"
    echo "Using: .venv/bin/python"
  else
    PYTHON="python3"
    echo "No .venv found; using: $PYTHON"
  fi
fi

echo "Python: $($PYTHON --version 2>&1)"
echo ""

echo "--- PyTorch & CUDA ---"
$PYTHON -c "
import sys
try:
    import torch
    print('PyTorch:', torch.__version__)
    print('CUDA available:', torch.cuda.is_available())
    if torch.cuda.is_available():
        print('CUDA version (build):', getattr(torch.version, 'cuda', 'N/A'))
        print('Device:', torch.cuda.get_device_name(0))
        for i in range(torch.cuda.device_count()):
            print('  GPU', i, ':', torch.cuda.get_device_name(i))
    else:
        print('(Running on CPU)')
except ImportError as e:
    print('torch not installed:', e)
    sys.exit(1)
"

echo ""
echo "--- Project deps (optional) ---"
$PYTHON -c "
try:
    import transformers; print('transformers:', transformers.__version__)
except ImportError: print('transformers: not installed')
try:
    import langchain_core; print('langchain_core: ok')
except ImportError: print('langchain_core: not installed')
try:
    import flask; print('flask: ok')
except ImportError: print('flask: not installed')
"

echo ""
echo "Done (no packages were installed)."
