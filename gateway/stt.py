"""
Speech-to-Text Gateway Adapter for Q-Doc MVP.
Integrates Sarvam AI Speech-to-Text with support for Indian languages (Hindi, English, etc.)
and browser Web Speech API fallback.
"""

import os
import requests
from typing import Optional, Dict, Any

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"

class STTGateway:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or SARVAM_API_KEY

    def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language_code: str = "hi-IN"
    ) -> Dict[str, Any]:
        """
        Transcribes audio using Sarvam STT API if key is present,
        otherwise signals client to use Web Speech API fallback.
        """
        if not self.api_key:
            return {
                "success": False,
                "provider": "browser_fallback",
                "message": "Sarvam API key not set. Using browser Web Speech API.",
                "transcript": ""
            }

        headers = {
            "api-subscription-key": self.api_key
        }

        try:
            files = {
                "file": (filename, audio_bytes, "audio/wav")
            }
            data = {
                "language_code": language_code,
                "model": "saaras:v1"
            }

            resp = requests.post(SARVAM_STT_URL, headers=headers, files=files, data=data, timeout=12.0)
            if resp.status_code == 200:
                result = resp.json()
                transcript = result.get("transcript", "")
                return {
                    "success": True,
                    "provider": "sarvam",
                    "transcript": transcript,
                    "language_code": language_code
                }
            else:
                return {
                    "success": False,
                    "provider": "sarvam_error",
                    "status_code": resp.status_code,
                    "message": resp.text,
                    "transcript": ""
                }
        except Exception as e:
            return {
                "success": False,
                "provider": "error",
                "message": str(e),
                "transcript": ""
            }
