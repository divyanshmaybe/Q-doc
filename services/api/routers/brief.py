"""
Clinician Brief router for Q-Doc MVP API.
Endpoints:
GET /api/v1/session/{id}/brief
GET /api/v1/briefs
POST /api/v1/session/{id}/brief/review
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from services.api.database import DatabaseRepo

router = APIRouter(tags=["brief"])

class DoctorReviewRequest(BaseModel):
    approved: bool
    notes: Optional[str] = ""
    overridden_diagnosis: Optional[str] = None

@router.get("/api/v1/session/{session_id}/brief")
def get_clinician_brief(session_id: str):
    brief_id = f"brief_{session_id}"
    brief = DatabaseRepo.get_brief(brief_id)
    if not brief:
        # Check by session_id directly
        with DatabaseRepo.get_connection() as conn:
            row = conn.execute("SELECT * FROM briefs WHERE session_id = ?", (session_id,)).fetchone()
            if row:
                import json
                d = dict(row)
                d["brief_data"] = json.loads(d["brief_json"])
                return d
        raise HTTPException(status_code=404, detail="Clinician brief not found for this session")
    return brief

@router.get("/api/v1/briefs")
def list_clinician_briefs():
    return DatabaseRepo.list_briefs()

@router.post("/api/v1/session/{session_id}/brief/review")
def review_clinician_brief(session_id: str, req: DoctorReviewRequest):
    brief_id = f"brief_{session_id}"
    brief = DatabaseRepo.get_brief(brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    notes_combined = req.notes or ""
    if req.overridden_diagnosis:
        notes_combined = f"[OVERRIDE: {req.overridden_diagnosis}] " + notes_combined

    DatabaseRepo.update_brief_review(brief_id, req.approved, notes_combined)
    return {
        "success": True,
        "brief_id": brief_id,
        "approved": req.approved,
        "message": "Doctor sign-off recorded successfully"
    }

