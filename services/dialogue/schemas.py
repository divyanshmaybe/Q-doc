"""
Shared Data Contracts & Schemas for Q-Doc MVP.
Strictly defines condition taxonomy, clinical intake slots,
image/reasoner outputs, and controllable policy verdicts.
"""

from enum import Enum
from typing import List, Optional, Dict, Union, Any
from pydantic import BaseModel, Field

class SkinCondition(str, Enum):
    ECZEMA = "eczema"
    PSORIASIS = "psoriasis"
    ACNE = "acne"
    URTICARIA = "urticaria"
    TINEA = "tinea"
    SCABIES = "scabies"
    ACANTHOSIS_NIGRICANS = "acanthosis_nigricans"
    VITILIGO = "vitiligo"
    MELASMA = "melasma"
    LICHEN_PLANUS = "lichen_planus"
    SEBORRHEIC_DERMATITIS = "seborrheic_dermatitis"
    CONTACT_DERMATITIS = "contact_dermatitis"
    OTHER_UNCLEAR = "other_unclear"              # Referral class
    POSSIBLE_MALIGNANCY = "possible_malignancy"  # Hard red-flag class

class UrgencyLevel(str, Enum):
    ROUTINE = "routine"
    SEEK_OPD = "seek_opd"
    EMERGENCY = "emergency"

class ClinicalIntakeSlots(BaseModel):
    primary_language: str = Field(default="hi-IN", description="Patient primary language code (hi-IN, en-IN)")
    age: Optional[int] = None
    sex: Optional[str] = None
    body_site: Optional[str] = Field(None, description="Location of lesion")
    lesion_type: Optional[str] = Field(None, description="Reported morphological description (e.g. rough and flaky skin, pimples, dark spot, rash)")
    duration_days: Optional[int] = Field(None, description="Duration in days")
    has_itching: Optional[bool] = None
    has_pain: Optional[bool] = None
    is_spreading: Optional[bool] = None
    has_fever: Optional[bool] = None
    household_contacts_affected: Optional[bool] = Field(None, description="Important for scabies")
    known_allergies: Optional[List[str]] = Field(default_factory=list)
    current_medications: Optional[List[str]] = Field(default_factory=list)
    
    # Dynamic clinical differential tracking
    suspected_differentials: List[str] = Field(default_factory=list, description="Top 3-5 conditions currently evaluated")
    condition_specific_history: Dict[str, Any] = Field(default_factory=dict, description="Tailored answers for specific conditions")
    primary_suspected_condition: Optional[str] = Field(None, description="Current leading clinical hypothesis")
    diagnostic_confidence: float = Field(default=0.0, description="Estimated diagnostic confidence")
    photo_image_id: Optional[str] = Field(None, description="Image ID of uploaded skin photograph")
    is_ready_for_photo: bool = Field(default=False, description="Whether agent has requested early photo capture")
    is_final_verdict_ready: bool = Field(default=False, description="Whether consultation has reached final diagnosis")

    # State tracking
    missing_required_slots: List[str] = Field(default_factory=list)
    is_complete: bool = False
    turn_count: int = 0

class ImagePrediction(BaseModel):
    probabilities: Dict[SkinCondition, float]
    top_condition: SkinCondition
    confidence: float
    image_quality_score: float # 0.0 to 1.0 (checks blur, brightness)
    quality_passed: bool

class DifferentialDiagnosisItem(BaseModel):
    condition: Union[SkinCondition, str]
    probability: float
    clinical_justification: str = Field(..., description="Must cite history or visual features")

class ClinicalReasonerOutput(BaseModel):
    differential: List[DifferentialDiagnosisItem]
    top_diagnosis: Union[SkinCondition, str]
    final_confidence: float
    identified_red_flags: List[str]
    synthesized_explanation: str
    baseline_image_top: Optional[Union[SkinCondition, str]] = None
    baseline_image_confidence: Optional[float] = None
    gain_from_voice_history: Optional[str] = None

class ActionVerdict(str, Enum):
    SPEAK_VERDICT = "speak_verdict"           # Autonomous verdict spoken
    REFER_ONLY = "refer_only"                 # Low confidence or red flag
    SUPERVISED_QUEUE = "supervised_queue"     # Supervised mode (held for clinician)
    RETAKE_IMAGE = "retake_image"             # Blurry/dark photo

class PolicyDecision(BaseModel):
    action: ActionVerdict
    abstain: bool
    urgency: UrgencyLevel
    spoken_patient_message: str
    doctor_brief_id: Optional[str] = None
    applied_rules: List[str]

