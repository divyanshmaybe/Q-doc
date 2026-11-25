"""Gemini JSON gateway for intake."""
import os
import json
import time
from contextvars import ContextVar
from typing import Callable
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from .errors import ProviderError
from .base import BaseLLMAdapter

load_dotenv()

from pydantic import Field
from services.dialogue.schemas import IntakeFacts

retry_notice: ContextVar[Optional[Callable[[int], None]]] = ContextVar("gemini_retry_notice", default=None)


def post_intake(url, headers, payload):
    for attempt in range(4):
        delay = 2 ** attempt
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=(5, 25))
        except (requests.Timeout, requests.ConnectionError):
            if attempt == 3:
                raise
        else:
            if response.status_code not in (408, 429, 500, 502, 503, 504) or attempt == 3:
                return response
            retry_after = response.headers.get("Retry-After", "")
            if retry_after:
                if not retry_after.isdecimal() or int(retry_after) > 30:
                    return response
                delay = max(delay, int(retry_after))
        notify = retry_notice.get()
        if notify:
            notify(attempt + 1)
        time.sleep(delay)


class IntakeReply(IntakeFacts):
    next_field: Optional[str] = None
    next_question: Optional[str] = None
    declined_current_question: bool = False
    answer_unknown: bool = False
    unknown_fields: list[str] = Field(default_factory=list)
    needs_reconfirmation: bool = False
    social_opening: bool = False
    summary_confirmed: Optional[bool] = None
    ambiguous_fields: list[str] = Field(default_factory=list)
    ambiguity_evidence: dict[str, str] = Field(default_factory=dict)


class LLMAdapter(BaseLLMAdapter):
    def __init__(self, api_key: Optional[str] = None):
        self.gemini_key = api_key or os.getenv("GEMINI_API_KEY", "")

    def generate_json(self, system_prompt: str, user_prompt: str, response_model=IntakeReply) -> Dict[str, Any]:
        if not self.gemini_key:
            raise ProviderError("Gemini failed: API key is missing.")
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        try:
            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"{system_prompt}\n\nCase / Input:\n{user_prompt}\n\nRespond with valid JSON only."}
                    ]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "responseJsonSchema": response_model.model_json_schema(),
                    "temperature": 0.1
                }
            }
            resp = post_intake(url, {"x-goog-api-key": self.gemini_key}, payload)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("\n", 1)[1]
                    if raw_text.endswith("```"):
                        raw_text = raw_text.rsplit("```", 1)[0]
                result = json.loads(raw_text.strip())
                if not isinstance(result, dict) or not result or result.get('status') == 'fallback':
                    raise ValueError('Unexpected model response')
                return response_model.model_validate(result, strict=True).model_dump(exclude_unset=True)
            raise ProviderError(f"Gemini failed (HTTP {resp.status_code}).")
        except requests.Timeout as exc:
            raise ProviderError("Gemini intake request timed out.") from exc
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
            raise ProviderError("Gemini failed to return a usable response.") from exc
