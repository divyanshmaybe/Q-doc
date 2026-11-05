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

    # Speech synthesis
    speech_res = tts_adapter.synthesize(welcome_text, language_code=req.language)

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

