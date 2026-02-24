# 环境配置 (Environment Setup)

适用于 Ubuntu 22.04 + NVIDIA RTX 3070 + CUDA 13 的 SSH 开发环境。

## 0. 已有 venv + 已装 PyTorch (如 cu130) 时

若你已经有一个 venv 并安装了 **cu130**（或其他版本）的 PyTorch，**不要**再跑 `setup_venv.sh`（会装 cu124，可能覆盖）。

**只做检查（不安装任何东西）：**

```bash
source .venv/bin/activate
bash scripts/check_venv.sh
```

会输出：当前 Python、PyTorch 版本、`torch.cuda.is_available()`、GPU 名称等。

**只安装项目其余依赖（不碰 torch）：**

```bash
source .venv/bin/activate
pip install -r requirements-no-torch.txt
```

`requirements-no-torch.txt` 里没有 `torch`，不会覆盖你已有的 cu130。若同一 venv 里还装了 **chronos-forecasting** 等要求 `transformers<5` 的包，已在该文件中将 transformers 限制为 `>=4.36.0,<5`，避免冲突。

---

## 1. 创建 venv 并安装依赖（含 GPU）

在仓库根目录执行：

```bash
bash scripts/setup_venv.sh
```

脚本会：

- 使用当前 `python3` 创建 `.venv`
- 先安装 **PyTorch (CUDA 12.4)**，再安装 `requirements.txt`
- 最后用 Python 检查 `torch.cuda.is_available()`

激活虚拟环境：

```bash
source .venv/bin/activate
```

## 2. 显卡与 CUDA 说明

- **CUDA 13**：当前 PyTorch 官方 wheel 多为 **cu121 / cu124**。驱动支持 CUDA 13 时，一般可向后兼容运行 cu124 的 PyTorch；若报错，可尝试安装系统级 CUDA 12.4 或使用 cu121。
- **指定 GPU**：多卡时可通过环境变量限制使用的卡，例如只用 0 号卡：

  ```bash
  export CUDA_VISIBLE_DEVICES=0
  ```

- **验证 GPU**：

  ```bash
  source .venv/bin/activate
  python -c "import torch; print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"
  ```

## 3. 环境变量（.env）

复制示例并按需修改：

```bash
cp .env.example .env
# 编辑 .env，至少设置 HF_TOKEN（Hugging Face 读模型用）
```

可选：在 `.env` 中增加（如需）：

```bash
# 仅使用第一块 GPU
CUDA_VISIBLE_DEVICES=0
```

## 4. 运行 Agent（简要）

```bash
source .venv/bin/activate
export PYTHONPATH=.:src
python scripts/run_agent_cli.py "What are Meta's ad policies for health?"
```

启动 Flask API：

```bash
source .venv/bin/activate
export PYTHONPATH=.:src
python -m api.app
```

## 5. 若使用不同 CUDA 版本

- **仅 CPU**：不运行 `setup_venv.sh` 中的 PyTorch 行，直接 `pip install -r requirements.txt`（会装 CPU 版 torch）。
- **CUDA 12.1**：在 `scripts/setup_venv.sh` 里把 `cu124` 改为 `cu121`，对应 index-url 改为 `https://download.pytorch.org/whl/cu121`。

## 6. 在 SSH 上运行

前提：已在 SSH 机器上装好 venv 和依赖（见上文），工作目录为仓库根目录。

**一次性：** 复制并编辑 `.env`（至少设置 `HF_TOKEN`），可选运行 `bash scripts/check_venv.sh` 确认环境。

**方式 A — 命令行跑 Agent（推荐先验证）**

无需先手动激活 venv 或设置 `PYTHONPATH`，脚本会自动处理（优先使用已激活的 venv，否则尝试 `./.venv` 或 `~/python-envs/normwear_env`，也可通过环境变量 `VENV_PATH` 指定）：

```bash
bash scripts/run_agent_ssh.sh "What are Meta's ad policies for health?"
bash scripts/run_agent_ssh.sh "Which platforms should I use for a 5000 monthly budget?"
```

首次运行会从 Hugging Face 下载模型和 embedding，耗时会较长。

**方式 B — 启动 Flask API**

```bash
bash scripts/run_flask_ssh.sh
```

服务监听 `0.0.0.0:5000`。在 SSH 本机测试：

```bash
curl http://localhost:5000/health
curl -X POST http://localhost:5000/agent -H "Content-Type: application/json" -d '{"question": "What are Meta ad policies for health?"}'
```

从本机（非 SSH）访问时，登录 SSH 时加端口转发：`ssh -L 5000:localhost:5000 user@ssh-host`，再在 SSH 上执行 `run_flask_ssh.sh`，本机访问 `http://localhost:5000`。

**常见问题：** `ModuleNotFoundError: marketing_agent / prompts` → 确保在仓库根目录执行上述脚本。未配置 `HF_TOKEN` 会导致读模型失败；CUDA OOM 可在 `.env` 中设 `CUDA_VISIBLE_DEVICES=0` 或换更小模型。

环境配置好后，可按 [README](../README.md) 和 plan 继续开发与联调。
