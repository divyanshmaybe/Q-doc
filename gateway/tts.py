"""
Text-to-Speech Gateway Adapter for Q-Doc MVP.
Integrates Sarvam AI TTS (Bulbul:v1) with support for Indian languages,
paired with browser SpeechSynthesis fallback.
"""

import os
import requests
from typing import Optional, Dict, Any

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

class TTSGateway:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or SARVAM_API_KEY

    def synthesize_speech(
        self,
        text: str,
        target_language_code: str = "hi-IN",
        speaker: str = "meera"
    ) -> Dict[str, Any]:
        """
        Synthesizes text into speech. Returns base64 audio if Sarvam API is active,
        or browser synthesis config instructions.
        """
        if not self.api_key:
            return {
                "success": True,
                "provider": "browser_speech_synthesis",
                "text": text,
                "language_code": target_language_code,
                "audio_base64": None
            }

        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": [text[:500]],
            "target_language_code": target_language_code,
            "speaker": speaker,
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": 22050,
            "enable_preprocessing": True,
            "model": "bulbul:v1"
        }

        try:
            resp = requests.post(SARVAM_TTS_URL, headers=headers, json=payload, timeout=12.0)
            if resp.status_code == 200:
                data = resp.json()
                audios = data.get("audios", [])
                audio_b64 = audios[0] if audios else None
                return {
                    "success": True,
                    "provider": "sarvam",
                    "text": text,
                    "audio_base64": audio_b64,
                    "language_code": target_language_code
                }
            else:
                return {
                    "success": False,
                    "provider": "browser_speech_synthesis",
                    "text": text,
                    "message": f"Sarvam error {resp.status_code}: {resp.text}",
                    "audio_base64": None
                }
        except Exception as e:
            return {
                "success": False,
                "provider": "browser_speech_synthesis",
                "text": text,
                "message": str(e),
                "audio_base64": None
            }
