"""
FastAPI entry point for Q-Doc MVP.
Integrates Session, Intake, Analysis, and Clinician Brief routers,
serves static frontend assets, and provides benchmark endpoints.
Fully supports both /api/v1/... and /api/... endpoints for compatibility.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

from services.api.database import init_db, DatabaseRepo
from services.api.routers import session, intake, analysis, brief
from eval.run_benchmarks import run_heldout_evaluation

# Initialize SQLite database
init_db()

app = FastAPI(
    title="Q-Doc MVP API",
    description="Voice-first and photo-based skin screening agent with controllable autonomy",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(session.router)
app.include_router(intake.router)
app.include_router(analysis.router)
app.include_router(brief.router)

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps", "web"))

@app.get("/api/v1/health")
@app.get("/api/health")
def api_health():
    from services.policy.rules import load_policy_config
    cfg = load_policy_config()
    return {
        "status": "healthy",
        "service": "Q-Doc MVP",
        "version": "1.0.0",
        "mode": cfg.get("mode", "autonomous")
    }

@app.get("/api/v1/image/{image_id}/file")
@app.get("/api/image/{image_id}/file")
def get_image_file(image_id: str):
    with DatabaseRepo.get_connection() as conn:
        row = conn.execute("SELECT file_path FROM images WHERE id = ?", (image_id,)).fetchone()
        if not row or not os.path.exists(row["file_path"]):
            raise HTTPException(status_code=404, detail="Image not found")
        return FileResponse(row["file_path"])

@app.get("/api/v1/eval/report")
@app.get("/api/eval/report")
def get_eval_report():
    return run_heldout_evaluation()

@app.get("/api/v1/demo/cases")
@app.get("/api/demo/cases")
def get_demo_cases():
    """
    Standard demo cases matching the 3-minute demo script and validation checklist.
    """
    return [
        {
            "id": "case-1-scabies-gain",
            "title": "Case 1: Proving 'Gain from Voice History' (Scabies)",
            "language": "en-IN",
            "utterance": "I have rash between my finger web spaces and on my wrists for 2 weeks with severe nocturnal itching. My brother living with me is also scratching all night.",
            "slots": {
                "body_site": "hands",
                "duration_days": 14,
                "has_itching": True,
                "has_fever": False,
                "household_contacts_affected": True
            },
            "condition": "scabies",
            "mode": "autonomous",
            "description": "Visual appearance looks ambiguous (eczema vs scabies), but voice intake of nocturnal itching & affected brother elevates scabies to top diagnosis."
        },
        {
            "id": "case-2-malignancy-redflag",
            "title": "Case 2: Safety Guardrail - Possible Malignancy (Always Refer)",
            "language": "en-IN",
            "utterance": "I have an asymmetric dark pigmented spot on my shoulder that has become darker and larger over the past three months.",
            "slots": {
                "body_site": "torso",
                "duration_days": 90,
                "has_itching": False,
                "has_fever": False,
                "household_contacts_affected": False
            },
            "condition": "possible_malignancy",
            "mode": "autonomous",
            "description": "System flags possible_malignancy red flag, immediately forces action=refer_only with urgency=seek_opd, and never offers reassurance."
        },
        {
            "id": "case-3-fever-rash",
            "title": "Case 3: Fever with Rash Red Flag (Emergency Referral)",
            "language": "en-IN",
            "utterance": "I have sudden red rashes all over my torso for two days along with 102 degrees high fever and chills.",
            "slots": {
                "body_site": "torso",
                "duration_days": 2,
                "has_itching": True,
                "has_fever": True,
                "household_contacts_affected": False
            },
            "condition": "urticaria",
            "mode": "autonomous",
            "description": "Fever reported with acute rash triggers fever_with_rash red flag and emergency referral."
        },
        {
            "id": "case-4-supervised-mode",
            "title": "Case 4: Controllable Autonomy (Supervised Mode Handover)",
            "language": "en-IN",
            "utterance": "I have dry itchy scaly patches on my inner elbows for 3 weeks.",
            "slots": {
                "body_site": "arms",
                "duration_days": 21,
                "has_itching": True,
                "has_fever": False,
                "household_contacts_affected": False
            },
            "condition": "eczema",
            "mode": "supervised",
            "description": "In Supervised mode, confident predictions are held in supervised_queue with message 'Doctor will review'."
        },
        {
            "id": "case-5-blurry-photo",
            "title": "Case 5: Quality Gate - Blurry Photo Rejection",
            "language": "en-IN",
            "utterance": "I have red bumps on my hands.",
            "slots": {
                "body_site": "hands",
                "duration_days": 5,
                "has_itching": True,
                "has_fever": False,
                "household_contacts_affected": False
            },
            "condition": "eczema",
            "mode": "autonomous",
            "is_blurry": True,
            "description": "Rejects blurry or dark photos with Laplacian variance < 100, prompting patient to retake."
        }
    ]

# Compatibility aliases
@app.post("/api/session")
def alias_session(body: session.StartSessionRequest):
    return session.start_session(body)

@app.post("/api/turn")
def alias_turn(body: intake.TextTurnRequest, session_id: str = Form(None)):
    sid = session_id or getattr(body, "session_id", None)
    if not sid:
        # Check in body if dict
        pass
    return intake.process_intake_turn(sid, body)

@app.post("/api/image")
def alias_image(session_id: str = Form(...), language: str = Form("hi-IN"), file: UploadFile = File(...)):
    return analysis.analyze_session(session_id=session_id, file=file)

@app.get("/api/briefs")
def alias_briefs():
    return brief.list_clinician_briefs()

@app.get("/api/brief/{brief_id}")
def alias_get_brief(brief_id: str):
    sid = brief_id.replace("brief_", "")
    return brief.get_clinician_brief(sid)

@app.post("/api/review")
def alias_review(body: Dict[str, Any] = Body(...)):
    sid = body.get("brief_id", "").replace("brief_", "")
    approved = body.get("approved", True)
    notes = body.get("notes", "")
    return brief.review_clinician_brief(sid, brief.DoctorReviewRequest(approved=approved, notes=notes))

@app.get("/api/policy/config")
def alias_policy_get():
    return session.get_admin_mode()

@app.post("/api/policy/config")
def alias_policy_post(body: Dict[str, Any] = Body(...)):
    mode = body.get("mode", "autonomous")
    return session.set_admin_mode(session.ModeToggleRequest(mode=mode))

# Mount static frontend at root (serves compiled Vite production bundle if built, else web root)
dist_dir = os.path.join(WEB_DIR, "dist")
if os.path.exists(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static_web")
elif os.path.exists(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="static_web")
