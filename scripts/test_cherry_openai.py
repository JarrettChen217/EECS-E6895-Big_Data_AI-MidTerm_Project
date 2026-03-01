#!/usr/bin/env python3
"""
独立测试脚本：用与后端相同的配置调用 Cherry Studio（OpenAI 兼容）接口。
用于排查 401 无效令牌等问题。

使用方式：
  1. 在项目根目录的 .env 中设置（Cherry Studio）：
     OPENAI_API_KEY=sk-xxxxxxxx
     OPENAI_BASE_URL=https://open.cherryin.net/v1
     OPENAI_MODEL=openai/gpt-5-chat
  2. 在项目根目录执行：python scripts/test_cherry_openai.py
"""

import os
import sys
from pathlib import Path

# 加载 .env（与 config 一致）
_root = Path(__file__).resolve().parent.parent
_dotenv = _root / ".env"
if _dotenv.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_dotenv, override=True)
    except ImportError:
        pass

API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()


def main():
    if not API_KEY:
        print("错误: 未设置 OPENAI_API_KEY。请在 .env 中配置或导出环境变量。", file=sys.stderr)
        print("示例: OPENAI_API_KEY=sk-xxxxxxxx", file=sys.stderr)
        sys.exit(1)

    print(f"BASE_URL: {BASE_URL}")
    print(f"MODEL:    {MODEL}")
    print(f"API_KEY:  {API_KEY[:8]}...{API_KEY[-4:] if len(API_KEY) > 12 else '***'}")
    print("-" * 50)

    try:
        from openai import OpenAI
    except ImportError:
        print("错误: 未安装 openai 包。请执行: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "你好，请用一句话介绍你自己"}],
        )
        text = (response.choices[0].message.content or "").strip()
        print("成功! 回复:", text)
    except Exception as e:
        print("请求失败:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
