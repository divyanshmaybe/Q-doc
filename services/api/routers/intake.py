"""
Intake turn router for Q-Doc MVP API.
Endpoint: POST /api/v1/session/{id}/turn
Takes audio binary or transcribed text, extracts clinical intake slots,
and returns agent voice response + updated slots + confirmation prompt.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import base64

from services.api.database import DatabaseRepo
from services.dialogue.schemas import ClinicalIntakeSlots
from services.dialogue.manager import DialogueManager
from services.dialogue.language import detect_language
from services.gateway.stt import SarvamSTTAdapter
from services.gateway.tts import SarvamTTSAdapter

router = APIRouter(tags=["intake"])
dialogue_manager = DialogueManager(max_turns=None)
stt_adapter = SarvamSTTAdapter()
tts_adapter = SarvamTTSAdapter()

class TextTurnRequest(BaseModel):
    transcript: str
    audio_base64: Optional[str] = None
    language: Optional[str] = None

@router.post("/api/v1/session/{session_id}/turn")
def process_intake_turn(
    session_id: str,
    req: TextTurnRequest
):
    sess = DatabaseRepo.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    turns = DatabaseRepo.get_session_turns(session_id)
    turn_idx = len(turns)
    session_lang = sess.get("language", "en-IN")
    req_lang = req.language or session_lang

    # 1. Transcript resolution
    transcript = req.transcript.strip()
    if not transcript and req.audio_base64:
        # Transcribe audio base64 via STT adapter
        try:
            audio_bytes = base64.b64decode(req.audio_base64)
            stt_res = stt_adapter.transcribe(audio_bytes, language_code=req_lang)
            transcript = stt_res.get("transcript", "")
        except Exception:
            transcript = ""

    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript or valid audio input required")

    # Dynamic Multilingual Language Detection & Auto-Switching
    # Switches automatically to Hindi if user speaks Hindi (Devanagari or Hinglish)
    # or to English if user speaks English.
    lang = detect_language(transcript, current_lang=req_lang)
    if lang != sess.get("language"):
        DatabaseRepo.update_session_language(session_id, lang)

    # Reconstruct current slots from history with the active language
    current_slots = ClinicalIntakeSlots(primary_language=lang)
    for t in turns:
        if t.get("slots"):
            for k, v in t["slots"].items():
                if hasattr(current_slots, k) and v is not None:
                    setattr(current_slots, k, v)
    current_slots.primary_language = lang

    # 2. Log patient turn
    DatabaseRepo.log_turn(session_id, turn_idx, "patient", transcript, current_slots.model_dump_json())

    # Detect last question context from prior agent turn
    last_question_slot = None
    if turns:
        agent_turns = [t for t in turns if t.get("speaker") == "agent"]
        if agent_turns:
            # Check the transcript of the last agent turn (using 'transcript' column)
            last_agent_text = (agent_turns[-1].get("transcript") or agent_turns[-1].get("text") or "").lower()
            if any(w in last_agent_text for w in ["fever", "chills", "बुखार", "temperature"]):
                last_question_slot = "has_fever"
            elif any(w in last_agent_text for w in ["household", "home", "family", "contacts", "परिवार", "घर"]):
                last_question_slot = "household_contacts_affected"
            elif any(w in last_agent_text for w in ["itch", "itching", "खुजली"]):
                last_question_slot = "has_itching"
            elif any(w in last_agent_text for w in ["how long", "days", "weeks", "year", "years", "month", "months", "कितने दिन", "हफ्ते", "साल"]):
                last_question_slot = "duration_days"
            elif any(w in last_agent_text for w in ["where", "part", "body", "किस हिस्से"]):
                last_question_slot = "body_site"

    # 3. Process turn via DialogueManager
    updated_slots, agent_msg, is_ready_for_photo, confirm_prompt = dialogue_manager.process_turn(
        current_slots=current_slots,
        user_utterance=transcript,
        last_question_slot=last_question_slot
    )

    # 4. Log agent turn
    DatabaseRepo.log_turn(session_id, turn_idx + 1, "agent", agent_msg, updated_slots.model_dump_json())

    # 5. Check if consultation has reached final diagnostic certainty
    verdict_data = None
    if updated_slots.is_final_verdict_ready and updated_slots.photo_image_id:
        try:
            from services.api.routers.analysis import analyze_session
            verdict_data = analyze_session(session_id, image_id=updated_slots.photo_image_id)
        except Exception as e:
            print(f"[IntakeRouter] Auto-analysis synthesis error: {e}")

    # 6. Synthesize TTS response
    speech_res = tts_adapter.synthesize(agent_msg, language_code=lang)

    return {
        "session_id": session_id,
        "transcript_received": transcript,
        "agent_response": agent_msg,
        "slots": updated_slots.model_dump(),
        "is_ready_for_photo": is_ready_for_photo,
        "is_final_verdict_ready": updated_slots.is_final_verdict_ready,
        "confirmation_prompt": confirm_prompt,
        "turn_count": updated_slots.turn_count,
        "missing_slots": updated_slots.missing_required_slots,
        "audio": speech_res,
        "language": lang,
        "verdict_data": verdict_data
    }

