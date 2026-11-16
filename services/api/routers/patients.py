"""Email-indexed patient history; each encounter retains its own evidence."""
import json
import re
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from services.api.database import DatabaseRepo, db_session

router = APIRouter(tags=["patients"])


def normalize_email(value):
    email = value.strip().casefold()
    if len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ValueError("Enter a valid email address")
    return email


class PatientEmail(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return normalize_email(value)


def initialize():
    with db_session() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS patient_sessions (
            session_id TEXT PRIMARY KEY, patient_id TEXT NOT NULL, linked_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS patient_sessions_patient ON patient_sessions(patient_id);
        """)
        conn.commit()


def link_patient(session_id, email):
    email = normalize_email(email)
    initialize()
    with db_session() as conn:
        conn.execute("BEGIN IMMEDIATE")
        if not conn.execute("SELECT id FROM sessions WHERE id=?", (session_id,)).fetchone():
            raise HTTPException(404, "Session not found")
        existing = conn.execute("SELECT p.* FROM patients p JOIN patient_sessions ps ON ps.patient_id=p.id WHERE ps.session_id=?", (session_id,)).fetchone()
        if existing and existing["email"] != email:
            raise HTTPException(409, "This consultation is already linked to another email. Start a new consultation for another patient.")
        conn.execute("INSERT OR IGNORE INTO patients VALUES (?,?,?)", (uuid.uuid4().hex, email, DatabaseRepo.now_iso()))
        patient = dict(conn.execute("SELECT * FROM patients WHERE email=?", (email,)).fetchone())
        conn.execute("INSERT OR IGNORE INTO patient_sessions VALUES (?,?,?)", (session_id, patient["id"], DatabaseRepo.now_iso()))
        conn.commit()
    return {"patient_id": patient["id"], "email": email, "session_id": session_id}


@router.post("/api/v1/session/{session_id}/patient")
def attach_patient(session_id: str, req: PatientEmail):
    return link_patient(session_id, req.email)


@router.post("/api/v1/patients/history")
def patient_history(req: PatientEmail):
    initialize()
    from services.api.routers.care import initialize as initialize_care
    initialize_care()
    with db_session() as conn:
        patient = conn.execute("SELECT * FROM patients WHERE email=?", (req.email,)).fetchone()
        if not patient:
            return {"patient_id": None, "email": req.email, "encounters": []}
        rows = conn.execute("""SELECT s.*, b.brief_json FROM sessions s
            JOIN patient_sessions ps ON ps.session_id=s.id
            LEFT JOIN briefs b ON b.session_id=s.id
            WHERE ps.patient_id=? ORDER BY s.created_at DESC""", (patient["id"],)).fetchall()
        encounters = []
        for row in rows:
            brief = json.loads(row["brief_json"]) if row["brief_json"] else {}
            followups = [json.loads(f["payload_json"]) for f in conn.execute(
                "SELECT payload_json FROM care_followups WHERE session_id=? ORDER BY rowid DESC", (row["id"],))]
            encounters.append({
                "session_id": row["id"], "created_at": row["created_at"], "language": row["language"],
                "screening_complete": bool(brief), "complaint": brief.get("chief_complaint_and_timeline"),
                "screening": brief.get("triage_verdict", {}),
                "condition_name": brief.get("clinical_reference", {}).get("coverage", {}).get("display_name"),
                "followups": followups,
            })
    return {"patient_id": patient["id"], "email": req.email, "encounters": encounters}
