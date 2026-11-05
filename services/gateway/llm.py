"""
LLM Gateway Adapter for Q-Doc MVP.
Supports Google Gemini, OpenAI, or Anthropic with strict JSON output,
with seamless fallback to the local Bayesian clinical engine.
"""

import os
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from .base import BaseLLMAdapter

load_dotenv()

class LLMAdapter(BaseLLMAdapter):
    def __init__(self, api_key: Optional[str] = None):
        self.gemini_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        # 1. Try Gemini if configured (targeting active available models with retry)
        if self.gemini_key:
            for model_name in [
                "gemini-3.1-flash-lite",
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash",
                "gemini-3.6-flash",
                "gemini-flash-latest"
            ]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.gemini_key}"
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": f"{system_prompt}\n\nCase / Input:\n{user_prompt}\n\nRespond with valid JSON only."}
                            ]
                        }],
                        "generationConfig": {
                            "responseMimeType": "application/json",
                            "temperature": 0.1
                        }
                    }
                    resp = requests.post(url, json=payload, timeout=10.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if raw_text.startswith("```"):
                            raw_text = raw_text.split("\n", 1)[1]
                            if raw_text.endswith("```"):
                                raw_text = raw_text.rsplit("```", 1)[0]
                        return json.loads(raw_text.strip())
                except Exception:
                    continue

        # 2. Try OpenAI if configured
        if self.openai_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2
                }
                resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=12.0)
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    return json.loads(content)
            except Exception:
                pass

        # 3. Try Anthropic if configured
        if self.anthropic_key:
            try:
                headers = {
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": f"{user_prompt}\n\nOutput ONLY valid JSON."}
                    ],
                    "temperature": 0.2
                }
                resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=12.0)
                if resp.status_code == 200:
                    raw_text = resp.json()["content"][0]["text"].strip()
                    if raw_text.startswith("```"):
                        raw_text = raw_text.split("\n", 1)[1]
                        if raw_text.endswith("```"):
                            raw_text = raw_text.rsplit("```", 1)[0]
                    return json.loads(raw_text.strip())
            except Exception:
                pass

        # 4. Deterministic local clinical Bayesian engine fallback
        return {
            "status": "fallback",
            "message": "Cloud LLM keys not provided or offline; using local calibrated Bayesian reasoner."
        }
