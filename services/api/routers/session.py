"""
Session management router for Q-Doc MVP API.
Endpoints:
POST /api/v1/session/start
GET /api/v1/session/{id}
POST /api/v1/admin/mode
GET /api/v1/admin/mode
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid

from services.api.database import DatabaseRepo
from services.dialogue.schemas import ClinicalIntakeSlots
from services.policy.rules import load_policy_config, save_policy_config
from services.gateway.tts import SarvamTTSAdapter

router = APIRouter(tags=["session"])
tts_adapter = SarvamTTSAdapter()

# In-memory and disk cache for instantaneous welcome greeting audio
import os, json
_WELCOME_AUDIO_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "gateway", ".cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

def _get_cached_welcome_audio(text: str, language_code: str) -> Dict[str, Any]:
    global _WELCOME_AUDIO_CACHE
    lang_key = "hi-IN" if "hi" in language_code.lower() else "en-IN"
    
    # 1. Check in-memory
    if lang_key in _WELCOME_AUDIO_CACHE and _WELCOME_AUDIO_CACHE[lang_key].get("audio_base64"):
        return _WELCOME_AUDIO_CACHE[lang_key]

    # 2. Check disk cache
    cache_file = os.path.join(_CACHE_DIR, f"welcome_{lang_key.replace('-', '_')}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("audio_base64"):
                    _WELCOME_AUDIO_CACHE[lang_key] = data
                    return data
        except Exception as e:
            print(f"[SessionRouter] Could not read disk audio cache: {e}")

    # 3. Synthesize via adapter
    speech_res = tts_adapter.synthesize(text, language_code=lang_key)
    if speech_res.get("success") and speech_res.get("audio_base64"):
        _WELCOME_AUDIO_CACHE[lang_key] = speech_res
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(speech_res, f)
        except Exception as e:
            print(f"[SessionRouter] Could not write disk audio cache: {e}")
    return speech_res

class StartSessionRequest(BaseModel):
    language: str = "en-IN"
    mode: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None

class ModeToggleRequest(BaseModel):
    mode: str # "autonomous" | "supervised"

@router.post("/api/v1/session/start")
def start_session(req: StartSessionRequest):
    cfg = load_policy_config()
    mode = req.mode or cfg.get("mode", "autonomous")
    session_id = str(uuid.uuid4())[:8]

    # Initialize in DB
    DatabaseRepo.create_session(session_id, language=req.language, mode=mode)

    # Initial Welcome with legal informed consent
    is_hi = "hi" in req.language.lower()
    if is_hi:
        welcome_text = (
            "नमस्ते, मैं क्यू-डॉक हूँ, आपका त्वचा स्क्रीनिंग सहायक। "
            "कृपया ध्यान दें: यह एक स्क्रीनिंग सहायता है, डॉक्टर नहीं। "
            "बताइए, आपकी त्वचा में क्या परेशानी हो रही है और यह किस अंग पर है?"
        )
    else:
        welcome_text = (
            "Hello, I am Q-Doc, your skin screening assistant. "
            "Please note: I am a screening aid, not a doctor. "
            "What skin issue are you experiencing, and where on your body is it located?"
        )

    # Log turn 0
    initial_slots = ClinicalIntakeSlots(primary_language=req.language, age=req.age, sex=req.sex)
    DatabaseRepo.log_turn(session_id, 0, "agent", welcome_text, initial_slots.model_dump_json())

    # Speech synthesis with instantaneous cache
    speech_res = _get_cached_welcome_audio(welcome_text, req.language)

    return {
        "session_id": session_id,
        "language": req.language,
        "mode": mode,
        "agent_message": welcome_text,
        "audio": speech_res,
        "slots": initial_slots.model_dump()
    }

@router.get("/api/v1/session/{session_id}")
def get_session(session_id: str):
    sess = DatabaseRepo.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    turns = DatabaseRepo.get_session_turns(session_id)
    return {
        "session": sess,
        "turns": turns
    }

@router.post("/api/v1/admin/mode")
def set_admin_mode(req: ModeToggleRequest):
    if req.mode not in ["autonomous", "supervised"]:
        raise HTTPException(status_code=400, detail="Mode must be 'autonomous' or 'supervised'")
    cfg = load_policy_config()
    cfg["mode"] = req.mode
    save_policy_config(cfg)
    return {"success": True, "mode": req.mode, "message": f"System mode switched to {req.mode.upper()}"}

@router.get("/api/v1/admin/mode")
def get_admin_mode():
    cfg = load_policy_config()
    return {"mode": cfg.get("mode", "autonomous"), "thresholds": cfg.get("thresholds", {})}

