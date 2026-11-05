"""
Sarvam AI TTS Adapter with Seamless Multi-Chunk Concatenation
and Browser SpeechSynthesis Fallback.
"""

import os
import re
import wave
import io
import base64
import requests
from typing import Dict, Any, Optional, List
from .base import BaseTTSAdapter

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"


def chunk_text_for_tts(text: str, max_chars: int = 400) -> List[str]:
    """Splits a long clinical paragraph into natural sentence chunks."""
    sentences = re.split(r"(?<=[.!?\n।])\s+", text.strip())
    chunks = []
    current = ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if len(current) + len(s) + 1 <= max_chars:
            current = f"{current} {s}".strip()
        else:
            if current:
                chunks.append(current)
            if len(s) > max_chars:
                parts = [s[i:i+max_chars] for i in range(0, len(s), max_chars)]
                chunks.extend(parts[:-1])
                current = parts[-1]
            else:
                current = s
    if current:
        chunks.append(current)
    return chunks or [text]


def concatenate_wav_audios(base64_list: List[str]) -> Optional[str]:
    """Seamlessly joins multiple base64-encoded WAV chunks into a single continuous WAV."""
    if not base64_list:
        return None
    if len(base64_list) == 1:
        return base64_list[0]

    try:
        in_buffers = [io.BytesIO(base64.b64decode(b)) for b in base64_list]
        wav_readers = [wave.open(b, "rb") for b in in_buffers]
        params = wav_readers[0].getparams()
        out_buf = io.BytesIO()

        with wave.open(out_buf, "wb") as wav_writer:
            wav_writer.setparams(params)
            for r in wav_readers:
                wav_writer.writeframes(r.readframes(r.getnframes()))
                r.close()

        return base64.b64encode(out_buf.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"[SarvamTTSAdapter] Error concatenating WAV audios: {e}")
        return base64_list[0]


class SarvamTTSAdapter(BaseTTSAdapter):
    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key

    @property
    def api_key(self) -> str:
        if self._explicit_key:
            return self._explicit_key.strip("'\" \t\r\n")
        try:
            from dotenv import load_dotenv
            load_dotenv(override=True)
        except Exception:
            pass
        raw = os.getenv("SARVAM_API_KEY", "")
        return raw.strip("'\" \t\r\n") if raw else ""

    def synthesize(self, text: str, language_code: str = "hi-IN") -> Dict[str, Any]:
        current_key = self.api_key
        if not current_key:
            return {
                "success": True,
                "provider": "browser_speech_synthesis",
                "text": text,
                "language_code": language_code,
                "audio_base64": None
            }

        headers = {
            "api-subscription-key": current_key,
            "Content-Type": "application/json"
        }

        speaker = (os.getenv("SARVAM_SPEAKER") or "rohan").strip("'\" \t\r\n")
        chunks = chunk_text_for_tts(text, max_chars=400)

        # Sarvam allows up to 3 chunks per POST request
        batch_size = 3
        batches = [chunks[i:i+batch_size] for i in range(0, len(chunks), batch_size)]

        all_audios: List[str] = []

        try:
            for b in batches:
                payload = {
                    "inputs": b,
                    "target_language_code": language_code,
                    "speaker": speaker,
                    "pitch": 0,
                    "pace": 1.0,
                    "loudness": 1.5,
                    "speech_sample_rate": 22050,
                    "enable_preprocessing": True,
                    "model": "bulbul:v3"
                }
                resp = requests.post(SARVAM_TTS_URL, headers=headers, json=payload, timeout=20.0)
                if resp.status_code == 200:
                    data = resp.json()
                    audios = data.get("audios", [])
                    all_audios.extend(audios)
                else:
                    print(f"[SarvamTTSAdapter] Batch error {resp.status_code}: {resp.text}")

            if all_audios:
                combined_b64 = concatenate_wav_audios(all_audios)
                return {
                    "success": True,
                    "provider": "sarvam",
                    "text": text,
                    "audio_base64": combined_b64,
                    "language_code": language_code
                }
            else:
                return {
                    "success": False,
                    "provider": "browser_speech_synthesis",
                    "text": text,
                    "error": "Failed to synthesize audio chunks",
                    "audio_base64": None
                }
        except Exception as e:
            return {
                "success": False,
                "provider": "browser_speech_synthesis",
                "text": text,
                "error": str(e),
                "audio_base64": None
            }

