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
import asyncio
from fastapi.responses import StreamingResponse
from services.gateway.llm import retry_notice

from services.api.database import DatabaseRepo
from services.dialogue.schemas import ClinicalIntakeSlots
from services.dialogue.state import restore_intake
from services.dialogue.manager import DialogueManager
from services.dialogue.language import detect_language
from services.gateway.errors import ProviderError
from services.gateway.stt import SarvamSTTAdapter
from services.gateway.tts import SarvamTTSAdapter

router = APIRouter(tags=["intake"])
dialogue_manager = DialogueManager(max_turns=None)
stt_adapter = SarvamSTTAdapter()
tts_adapter = SarvamTTSAdapter()

class TextTurnRequest(BaseModel):
    transcript: str
    defer_audio: bool = False
    audio_base64: Optional[str] = None
    language: Optional[str] = None


@router.post("/api/v1/session/{session_id}/turn/stream")
async def stream_intake_turn(session_id: str, req: TextTurnRequest):
    events = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def publish(event):
        loop.call_soon_threadsafe(events.put_nowait, event)

    def run():
        token = retry_notice.set(lambda number: publish({"retry": number}))
        try:
            publish({"result": process_intake_turn(session_id, req)})
        except ProviderError as exc:
            publish({"error": str(exc)})
        except HTTPException as exc:
            publish({"error": exc.detail})
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Intake turn failed")
            publish({"error": "The intake request failed."})
        finally:
            retry_notice.reset(token)

    async def stream():
        worker = asyncio.create_task(asyncio.to_thread(run))
        try:
            while True:
                event = await events.get()
                yield json.dumps(event) + "\n"
                if "retry" not in event:
                    break
        finally:
            await worker

    return StreamingResponse(stream(), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})

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

    # Reconstruct current slots from history
    current_slots = restore_intake(turns, req_lang)

    # 1. Transcript resolution
    transcript = req.transcript.strip()
    if not transcript and req.audio_base64:
        # Transcribe audio base64 via STT adapter
        try:
            audio_bytes = base64.b64decode(req.audio_base64)
            stt_res = stt_adapter.transcribe(audio_bytes, language_code=req_lang)
            if not stt_res.get("success"):
                raise ProviderError("Sarvam speech recognition failed.")
            transcript = stt_res.get("transcript", "").strip()
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError("Sarvam speech recognition failed.") from exc

    # If no speech was captured (e.g. ambient silence or pause), respond politely without error
    if not transcript:
        is_hi = "hi" in req_lang.lower()
        fallback_msg = (
            "माफ़ कीजिए, मुझे आपकी आवाज़ स्पष्ट नहीं आई। कृपया अपनी त्वचा के लक्षणों के बारे में दोबारा बताएं या नीचे लिखें।"
            if is_hi
            else "I didn't catch that clearly. Please tell me about your skin symptoms or type them below."
        )
        return {
            "session_id": session_id,
            "agent_response": fallback_msg,
            "slots": current_slots.model_dump(),
            "turn_index": turn_idx,
            "language": req_lang,
            "audio": tts_adapter.synthesize(fallback_msg, language_code=req_lang),
            "is_ready_for_photo": False
        }

    # Dynamic Multilingual Language Detection & Auto-Switching
    # Switches automatically to Hindi if user speaks Hindi (Devanagari or Hinglish)
    # or to English if user speaks English.
    lang = detect_language(transcript, current_lang=req_lang)
    if lang != sess.get("language"):
        DatabaseRepo.update_session_language(session_id, lang)

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
        last_question_slot=last_question_slot,
        turn_history=turns
    )

    # 4. Log agent turn
    DatabaseRepo.log_turn(session_id, turn_idx + 1, "agent", agent_msg, updated_slots.model_dump_json())

    # 5. Check if consultation has reached final diagnostic certainty
    verdict_data = None
    if updated_slots.is_final_verdict_ready and updated_slots.photo_image_id:
        try:
            from services.api.routers.analysis import analyze_session
            verdict_data = analyze_session(session_id, image_id=updated_slots.photo_image_id)
        except ProviderError:
            raise
        except Exception as e:
            print(f"[IntakeRouter] Auto-analysis synthesis error: {e}")

    if verdict_data:
        agent_msg = verdict_data["policy_decision"]["spoken_patient_message"]
        updated_slots = restore_intake(DatabaseRepo.get_session_turns(session_id), lang)

    if verdict_data:
        speech_res = verdict_data["audio"]
    else:
        speech_res = None if req.defer_audio else tts_adapter.synthesize(agent_msg, language_code=lang)

    return {
        "session_id": session_id,
        "transcript_received": transcript,
        "agent_response": agent_msg,
        "audio_turn_index": turn_idx + (2 if verdict_data else 1),
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


@router.post("/api/v1/session/{session_id}/turn/{turn_index}/speech")
def synthesize_turn(session_id: str, turn_index: int):
    for turn in DatabaseRepo.get_session_turns(session_id):
        if turn["turn_index"] == turn_index and turn["speaker"] == "agent":
            return tts_adapter.synthesize(turn["transcript"], language_code=turn["slots"].get("primary_language") or "en-IN")
    raise HTTPException(status_code=404, detail="Reply not found")

