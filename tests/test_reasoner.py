import pytest
import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.dialogue.schemas import (
    SkinCondition,
    ClinicalIntakeSlots,
    ImagePrediction
)
from services.reasoner.engine import ClinicalReasonerEngine

def test_closed_condition_list():
    reasoner = ClinicalReasonerEngine()
    assert len(reasoner.allowed_conditions) == 8
    assert SkinCondition.ACNE in reasoner.allowed_conditions
    assert SkinCondition.SCABIES in reasoner.allowed_conditions
    assert SkinCondition.POSSIBLE_MALIGNANCY in reasoner.allowed_conditions
    assert SkinCondition.OTHER_UNCLEAR in reasoner.allowed_conditions

def test_voice_history_gain_scabies():
    reasoner = ClinicalReasonerEngine()

    img_probs = {c: 0.05 for c in SkinCondition}
    img_probs[SkinCondition.ECZEMA] = 0.50
    img_probs[SkinCondition.SCABIES] = 0.25

    img_pred = ImagePrediction(
        probabilities=img_probs,
        top_condition=SkinCondition.ECZEMA,
        confidence=0.50,
        image_quality_score=0.90,
        quality_passed=True
    )

    intake = ClinicalIntakeSlots(
        primary_language="en-IN",
        body_site="hands",
        duration_days=14,
        has_itching=True,
        household_contacts_affected=True
    )

    result = reasoner.reason(intake=intake, img_pred=img_pred)
    assert result.top_diagnosis == SkinCondition.SCABIES
    assert result.final_confidence > 0.65
    assert result.baseline_image_top == SkinCondition.ECZEMA
    assert result.gain_from_voice_history is not None
