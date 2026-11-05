"""
Database ORM Models and Schemas for Q-Doc MVP.
Defines sessions, turns, images, predictions, policy_decisions, and briefs.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SessionRecord(BaseModel):
    id: str
    language: str = "en-IN"
    mode: str = "autonomous"
    status: str = "active"
    created_at: str
    updated_at: str

class TurnRecord(BaseModel):
    id: Optional[int] = None
    session_id: str
    turn_index: int
    speaker: str # "patient" or "agent"
    transcript: str
    slots_json: str
    timestamp: str

class ImageRecord(BaseModel):
    id: str
    session_id: str
    file_path: str
    quality_score: float
    blur_score: float
    brightness_score: float
    quality_passed: bool
    created_at: str

class PredictionRecord(BaseModel):
    id: Optional[int] = None
    session_id: str
    image_id: str
    top_condition: str
    confidence: float
    differential_json: str
    created_at: str

class PolicyDecisionRecord(BaseModel):
    id: Optional[int] = None
    session_id: str
    mode: str
    action: str
    abstain: bool
    urgency: str
    spoken_patient_message: str
    applied_rules_json: str
    created_at: str

class BriefRecord(BaseModel):
    id: str
    session_id: str
    brief_json: str
    doctor_approved: Optional[bool] = None
    doctor_notes: Optional[str] = None
    created_at: str

