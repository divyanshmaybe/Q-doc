"""
Image upload, analysis & policy triage router for Q-Doc MVP API.
Endpoints:
POST /api/v1/session/{id}/photo
POST /api/v1/session/{id}/analyze
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import os
import json

from services.api.database import DatabaseRepo, db_session
from services.clinical_knowledge.dermatology_kb import DermatologyKnowledgeService
from services.dialogue.schemas import (
    SkinCondition,
    ClinicalIntakeSlots,
    ImagePrediction,
    ClinicalReasonerOutput,
    PolicyDecision
)
from services.ml.classifier import SkinClassifierPipeline
from services.ml.quality import ImageQualityChecker
from services.reasoner.engine import ClinicalReasonerEngine
from services.reasoner.multimodal_agent import MultimodalDermatologistAgent
from services.policy.evaluator import PolicyEvaluator
from services.gateway.tts import SarvamTTSAdapter

router = APIRouter(tags=["analysis"])

classifier_pipeline = SkinClassifierPipeline()
quality_checker = ImageQualityChecker()
reasoner_engine = ClinicalReasonerEngine()
multimodal_agent = MultimodalDermatologistAgent()
policy_evaluator = PolicyEvaluator()
tts_adapter = SarvamTTSAdapter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/api/v1/session/{session_id}/photo")
def upload_photo(
    session_id: str,
    file: UploadFile = File(...)
):
    sess = DatabaseRepo.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    image_bytes = file.file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image upload")

    # 1. Run image quality check
    quality_res = quality_checker.evaluate_image_bytes(image_bytes)

    # 2. Save image file
    image_id = f"img_{uuid.uuid4().hex[:10]}"
    ext = os.path.splitext(file.filename or "skin.jpg")[1] or ".jpg"
    filename = f"{image_id}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, filename)

    with open(saved_path, "wb") as f:
        f.write(image_bytes)

    # 3. Log image record in DB
    DatabaseRepo.save_image_record(
        image_id=image_id,
        session_id=session_id,
        file_path=saved_path,
        quality_score=quality_res["quality_score"],
        blur_score=quality_res["blur_score"],
        brightness_score=quality_res["brightness_score"],
        quality_passed=quality_res["quality_passed"]
    )

    # Rejection guidance if blurred or low quality
    if not quality_res["quality_passed"]:
        is_hi = "hi" in sess.get("language", "hi-IN").lower()
        msg = quality_res["guidance_hi"] if is_hi else quality_res["guidance_en"]
        return {
            "session_id": session_id,
            "image_id": image_id,
            "quality": quality_res,
            "quality_passed": False,
            "action": "retake_image",
            "message": msg
        }

    # 4. Multimodal Visual Inspection for Early Image Intake
    # Reconstruct slots from session history
    turns = DatabaseRepo.get_session_turns(session_id)
    lang = sess.get("language", "en-IN")
    intake = ClinicalIntakeSlots(primary_language=lang)
    for t in turns:
        if t.get("slots"):
            for k, v in t["slots"].items():
                if hasattr(intake, k) and v is not None:
                    setattr(intake, k, v)
    intake.primary_language = lang

    # Inspect early photograph with Gemini Multimodal Vision
    early_res = multimodal_agent.inspect_early_photo(
        image_bytes=image_bytes,
        intake=intake,
        language=lang
    )

    # Update intake slots with image ID and visual hypotheses
    intake.photo_image_id = image_id
    intake.condition_specific_history["visual_morphology"] = early_res.get("visual_morphology")
    intake.suspected_differentials = early_res.get("candidate_differentials", [])
    intake.primary_suspected_condition = early_res.get("primary_hypothesis")
    intake.diagnostic_confidence = early_res.get("initial_confidence", 0.65)
    intake.is_ready_for_photo = False

    agent_q = early_res.get("agent_question", "Photo received and examined.")
    turn_idx = len(turns)
    DatabaseRepo.log_turn(session_id, turn_idx + 1, "agent", agent_q, intake.model_dump_json())

    # Synthesize audio for the agent's targeted question
    speech_res = tts_adapter.synthesize(agent_q, language_code=lang)

    return {
        "session_id": session_id,
        "image_id": image_id,
        "quality": quality_res,
        "quality_passed": True,
        "message": "Image accepted with good sharpness and lighting.",
        "agent_question": agent_q,
        "audio": speech_res,
        "slots": intake.model_dump(),
        "suspected_differentials": early_res.get("candidate_differentials", []),
        "photo_analyzed": True
    }

@router.post("/api/v1/session/{session_id}/analyze")
def analyze_session(
    session_id: str,
    image_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    sess = DatabaseRepo.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    lang = sess.get("language", "hi-IN")
    image_bytes = None
    saved_image_id = image_id

    # If file uploaded directly in analyze
    if isinstance(file, UploadFile):
        image_bytes = file.file.read()
        saved_image_id = f"img_{uuid.uuid4().hex[:10]}"
        ext = os.path.splitext(file.filename or "skin.jpg")[1] or ".jpg"
        saved_path = os.path.join(UPLOAD_DIR, f"{saved_image_id}{ext}")
        with open(saved_path, "wb") as f:
            f.write(image_bytes)
        q_res = quality_checker.evaluate_image_bytes(image_bytes)
        DatabaseRepo.save_image_record(
            image_id=saved_image_id,
            session_id=session_id,
            file_path=saved_path,
            quality_score=q_res["quality_score"],
            blur_score=q_res["blur_score"],
            brightness_score=q_res["brightness_score"],
            quality_passed=q_res["quality_passed"]
        )
    elif saved_image_id and isinstance(saved_image_id, str):
        # Load from disk
        with db_session() as conn:
            row = conn.execute("SELECT file_path FROM images WHERE id = ?", (saved_image_id,)).fetchone()
            if row and os.path.exists(row["file_path"]):
                with open(row["file_path"], "rb") as f:
                    image_bytes = f.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Skin photograph required for analysis")

    # 1. Run classifier & quality
    img_pred = classifier_pipeline.predict(image_bytes)

    # 2. Gather clinical intake slots
    turns = DatabaseRepo.get_session_turns(session_id)
    intake = ClinicalIntakeSlots(primary_language=lang)
    for t in turns:
        if t.get("slots"):
            for k, v in t["slots"].items():
                if hasattr(intake, k) and v is not None:
                    setattr(intake, k, v)

    # 3. Multimodal Diagnostic AI (Direct image examination + voice history + web search grounding)
    reasoner_output = multimodal_agent.diagnose(
        image_bytes=image_bytes,
        intake=intake,
        classifier_pred=img_pred,
        language=lang
    )

    # 4. Policy Evaluator
    policy_decision = policy_evaluator.evaluate(
        intake=intake,
        img_pred=img_pred,
        reasoning=reasoner_output
    )

    top_diag_val = (
        reasoner_output.top_diagnosis.value
        if hasattr(reasoner_output.top_diagnosis, "value")
        else str(reasoner_output.top_diagnosis)
    )

    # 5. Log prediction & policy decision in DB
    DatabaseRepo.log_prediction(
        session_id=session_id,
        image_id=saved_image_id or "unknown",
        top_cond=top_diag_val,
        conf=reasoner_output.final_confidence,
        differential=[d.model_dump() for d in reasoner_output.differential]
    )

    DatabaseRepo.log_policy_decision(
        session_id=session_id,
        mode=policy_evaluator.cfg.get("mode", "autonomous"),
        action=policy_decision.action.value,
        abstain=policy_decision.abstain,
        urgency=policy_decision.urgency.value,
        spoken_msg=policy_decision.spoken_patient_message,
        applied_rules=policy_decision.applied_rules
    )

    # 6. Generate and save 1-page Clinician Brief with In-Depth Dermatology KB
    top_cond = reasoner_output.top_diagnosis
    kb_info = DermatologyKnowledgeService.get_condition_info(top_cond)

    chief_complaint = f"Rash on {intake.body_site or 'lesion site'} for {intake.duration_days or 'several'} days"
    brief_data = {
        "session_id": session_id,
        "patient_metadata": {
            "age": intake.age or "Adult",
            "sex": intake.sex or "Unspecified",
            "primary_language": intake.primary_language
        },
        "chief_complaint_and_timeline": chief_complaint,
        "history_slots": intake.model_dump(),
        "lesion_image_id": saved_image_id,
        "clinical_reference": {
            "name": kb_info.get("name_en"),
            "name_hi": kb_info.get("name_hi"),
            "icd10": kb_info.get("icd10"),
            "pathophysiology": kb_info.get("pathophysiology"),
            "primary_lesions": kb_info.get("primary_lesions", []),
            "secondary_lesions": kb_info.get("secondary_lesions", []),
            "differentials": kb_info.get("differentials", []),
            "red_flags": kb_info.get("red_flags", []),
            "patient_guidance_en": kb_info.get("patient_guidance", {}).get("en", ""),
            "patient_guidance_hi": kb_info.get("patient_guidance", {}).get("hi", "")
        },
        "triage_verdict": {
            "top_diagnosis": top_diag_val,
            "final_confidence": f"{reasoner_output.final_confidence:.1%}",
            "confidence": reasoner_output.final_confidence,
            "urgency": policy_decision.urgency.value.upper(),
            "action": policy_decision.action.value,
            "abstain": policy_decision.abstain,
            "gain_from_voice_history": reasoner_output.gain_from_voice_history,
            "applied_safety_rules": policy_decision.applied_rules,
            "patient_spoken_message": policy_decision.spoken_patient_message,
        },
        "ranked_differential": [d.model_dump() for d in reasoner_output.differential],
        "detected_red_flags": reasoner_output.identified_red_flags,
        "exact_spoken_patient_transcript": policy_decision.spoken_patient_message,
        "applied_rules": policy_decision.applied_rules,
        "created_at": DatabaseRepo.now_iso()
    }
    brief_id = DatabaseRepo.save_brief(session_id, brief_data)
    policy_decision.doctor_brief_id = brief_id

    # 7. Synthesize audio for patient
    speech_res = tts_adapter.synthesize(
        policy_decision.spoken_patient_message,
        language_code=lang
    )

    return {
        "session_id": session_id,
        "image_id": saved_image_id,
        "image_prediction": img_pred.model_dump(),
        "reasoner_output": reasoner_output.model_dump(),
        "policy_decision": policy_decision.model_dump(),
        "audio": speech_res,
        "doctor_brief_id": brief_id
    }
