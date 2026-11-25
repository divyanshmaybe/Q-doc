import base64
import io
import wave
from unittest.mock import Mock

import pytest

from services.gateway import tts
from services.gateway.errors import ProviderError


def test_long_reply_retries_only_missing_piece(monkeypatch):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setparams((1, 2, 22050, 0, "NONE", ""))
        wav.writeframes(b"\x01\x00" * 20)
    clip = base64.b64encode(buf.getvalue()).decode()
    responses = iter(([clip], [], [clip]))
    post = Mock(side_effect=lambda *args, **kwargs: Mock(status_code=200, json=lambda: {"audios": next(responses)}))
    monkeypatch.setattr(tts.requests, "post", post)
    monkeypatch.setattr(tts.time, "sleep", lambda _: None)
    text = ("This is a test of the spoken closing summary. " * 60).strip()
    result = tts.SarvamTTSAdapter("test").synthesize(text, "en-IN")
    first, second, retry = [call.kwargs["json"] for call in post.call_args_list]
    assert second == retry
    assert first["text"] + " " + second["text"] == text
    assert first["language_code"] == "en-IN"
    with wave.open(io.BytesIO(base64.b64decode(result["audio_base64"]))) as wav:
        assert wav.getnframes() == round(22050 * .35) + 40


def test_persistently_empty_audio_is_reported(monkeypatch):
    post = Mock(return_value=Mock(status_code=200, json=lambda: {"audios": [""]}))
    monkeypatch.setattr(tts.requests, "post", post)
    monkeypatch.setattr(tts.time, "sleep", lambda _: None)
    with pytest.raises(ProviderError, match="incomplete audio after 4 attempts"):
        tts.SarvamTTSAdapter("test").synthesize("Hello")
    assert post.call_count == 4
