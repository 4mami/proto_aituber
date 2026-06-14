from __future__ import annotations
import asyncio
from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig


class HFClient:
    def __init__(self, model_id: str, lora_path: Optional[str] = None, quantize: Optional[str] = "4bit"):
        self._model_id = model_id
        self._lora_path = lora_path
        self._quantize = quantize
        self._tokenizer = None
        self._model = None

    def load(self) -> None:
        bnb_config = None
        if self._quantize == "4bit":
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
        elif self._quantize == "8bit":
            bnb_config = BitsAndBytesConfig(load_in_8bit=True)

        self._tokenizer = AutoTokenizer.from_pretrained(self._model_id)
        self._model = AutoModelForCausalLM.from_pretrained(
            self._model_id,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16 if bnb_config is None else None,
        )

        if self._lora_path:
            from peft import PeftModel
            self._model = PeftModel.from_pretrained(self._model, self._lora_path)

        self._model.eval()

    def _generate_sync(self, system: str, user: str) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        input_ids = self._tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(self._model.device)

        with torch.no_grad():
            output_ids = self._model.generate(
                input_ids,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        new_tokens = output_ids[0][input_ids.shape[-1]:]
        return self._tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    async def generate(self, system: str, user: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._generate_sync, system, user)
