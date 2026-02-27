"""Hugging Face Transformers LLM backend."""

from __future__ import annotations

import os
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from marketing_agent.llm.base import BaseLLM
from marketing_agent import config as agent_config


class HuggingFaceLLM(BaseLLM):
    """LLM using Hugging Face transformers (e.g. Qwen)."""

    def __init__(
        self,
        model_name: str | None = None,
        token: str | None = None,
        device_map: str = "auto",
        torch_dtype: torch.dtype | None = None,
    ) -> None:
        model_name = model_name or agent_config.HF_MODEL_NAME
        token = token or agent_config.HF_TOKEN or os.environ.get("HF_TOKEN", "")
        if torch_dtype is None:
            torch_dtype = torch.float16
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            token=token or None,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            device_map=device_map,
            dtype=torch_dtype,
            token=token or None,
        )

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        max_new_tokens: int = 256,
        temperature: float = 0.0,
        top_p: float = 0.95,
        top_k: int = 50,
        **kwargs: Any,
    ) -> str:
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        do_sample = temperature > 0.0
        gen_kwargs: dict[str, Any] = {
            **inputs,
            "max_new_tokens": max_new_tokens,
            "do_sample": do_sample,
            "pad_token_id": self.tokenizer.eos_token_id,
        }
        if do_sample:
            gen_kwargs["temperature"] = temperature
            gen_kwargs["top_p"] = top_p
            gen_kwargs["top_k"] = top_k

        with torch.inference_mode():
            outputs = self.model.generate(**gen_kwargs)

        input_len = inputs["input_ids"].shape[-1]
        new_ids = outputs[0][input_len:]
        text = self.tokenizer.decode(new_ids, skip_special_tokens=True).strip()
        return text
