"""
Sarvam AI STT Adapter with Browser WebSpeech API Fallback.
"""

import os
import requests
from typing import Dict, Any, Optional
from .base import BaseSTTAdapter

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"

class SarvamSTTAdapter(BaseSTTAdapter):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SARVAM_API_KEY", "")

    def transcribe(self, audio_bytes: bytes, language_code: str = "hi-IN") -> Dict[str, Any]:
        if not self.api_key:
            return {
                "success": False,
                "provider": "webspeech_fallback",
                "message": "SARVAM_API_KEY not configured. Falling back to browser Web Speech API.",
                "transcript": ""
            }

        headers = {
            "api-subscription-key": self.api_key
        }

        try:
            # Detect audio type from header magic bytes
            ext = "wav"
            mime = "audio/wav"
            if len(audio_bytes) > 4:
                if audio_bytes[:4] == b'\x1aE\xdf\xa3':
                    ext = "webm"
                    mime = "audio/webm"
                elif audio_bytes[:4] == b'OggS':
                    ext = "ogg"
                    mime = "audio/ogg"
                elif audio_bytes[:3] == b'ID3' or audio_bytes[:2] == b'\xff\xfb':
                    ext = "mp3"
                    mime = "audio/mpeg"
                elif b'ftyp' in audio_bytes[:12]:
                    ext = "mp4"
                    mime = "audio/mp4"

            files = {
                "file": (f"audio.{ext}", audio_bytes, mime)
            }
            data = {
                "language_code": language_code,
                "model": "saaras:v3"
            }
            resp = requests.post(SARVAM_STT_URL, headers=headers, files=files, data=data, timeout=12.0)
            if resp.status_code == 200:
                res_json = resp.json()
                return {
                    "success": True,
                    "provider": "sarvam",
                    "transcript": res_json.get("transcript", ""),
                    "language_code": language_code
                }
            else:
                return {
                    "success": False,
                    "provider": "webspeech_fallback",
                    "error": f"Sarvam HTTP {resp.status_code}: {resp.text}",
                    "transcript": ""
                }
        except Exception as e:
            return {
                "success": False,
                "provider": "webspeech_fallback",
                "error": str(e),
                "transcript": ""
            }

