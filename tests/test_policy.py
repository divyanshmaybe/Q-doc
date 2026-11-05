import pytest
import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.dialogue.schemas import (
    SkinCondition,
    UrgencyLevel,
    ClinicalIntakeSlots,
    ImagePrediction,
    DifferentialDiagnosisItem,
    ClinicalReasonerOutput,
    ActionVerdict
)
from services.policy.evaluator import PolicyEvaluator
from services.policy.rules import load_policy_config, save_policy_config, sanitize_safety_constraints

def test_autonomous_mode_confident():
    evaluator = PolicyEvaluator()
    cfg = load_policy_config()
    cfg["mode"] = "autonomous"
    save_policy_config(cfg)
    evaluator.reload_config()

    intake = ClinicalIntakeSlots(primary_language="en-IN", body_site="face", duration_days=10)
    img_pred = ImagePrediction(
        probabilities={SkinCondition.ACNE: 0.88, SkinCondition.ECZEMA: 0.08},
        top_condition=SkinCondition.ACNE,
        confidence=0.88,
        image_quality_score=0.90,
        quality_passed=True
    )
    reasoning = ClinicalReasonerOutput(
        differential=[
            DifferentialDiagnosisItem(condition=SkinCondition.ACNE, probability=0.88, clinical_justification="Facial acne"),
            DifferentialDiagnosisItem(condition=SkinCondition.ECZEMA, probability=0.08, clinical_justification="Minor")
        ],
        top_diagnosis=SkinCondition.ACNE,
        final_confidence=0.88,
        identified_red_flags=[],
        synthesized_explanation="Acne Vulgaris detected. Keep face clean with gentle cleanser."
    )

    decision = evaluator.evaluate(intake=intake, img_pred=img_pred, reasoning=reasoning)
    assert decision.action == ActionVerdict.SPEAK_VERDICT
    assert decision.abstain is False

def test_supervised_mode_switch():
    evaluator = PolicyEvaluator()
    cfg = load_policy_config()
    cfg["mode"] = "supervised"
    save_policy_config(cfg)
    evaluator.reload_config()

    intake = ClinicalIntakeSlots(primary_language="en-IN", body_site="elbows", duration_days=90)
    img_pred = ImagePrediction(
        probabilities={SkinCondition.PSORIASIS: 0.85, SkinCondition.ECZEMA: 0.10},
        top_condition=SkinCondition.PSORIASIS,
        confidence=0.85,
        image_quality_score=0.90,
        quality_passed=True
    )
    reasoning = ClinicalReasonerOutput(
        differential=[
            DifferentialDiagnosisItem(condition=SkinCondition.PSORIASIS, probability=0.85, clinical_justification="Plaques"),
            DifferentialDiagnosisItem(condition=SkinCondition.ECZEMA, probability=0.10, clinical_justification="Minor")
        ],
        top_diagnosis=SkinCondition.PSORIASIS,
        final_confidence=0.85,
        identified_red_flags=[],
        synthesized_explanation="Psoriasis suspected."
    )

    decision = evaluator.evaluate(intake=intake, img_pred=img_pred, reasoning=reasoning)
    assert decision.action == ActionVerdict.SUPERVISED_QUEUE
    assert "doctor will review" in decision.spoken_patient_message.lower() or "डॉक्टर" in decision.spoken_patient_message

    # Reset
    cfg["mode"] = "autonomous"
    save_policy_config(cfg)

def test_low_quality_abstention():
    evaluator = PolicyEvaluator()
    intake = ClinicalIntakeSlots(primary_language="en-IN")
    img_pred = ImagePrediction(
        probabilities={SkinCondition.ECZEMA: 0.85},
        top_condition=SkinCondition.ECZEMA,
        confidence=0.85,
        image_quality_score=0.35, # below 0.50
        quality_passed=False
    )
    reasoning = ClinicalReasonerOutput(
        differential=[],
        top_diagnosis=SkinCondition.ECZEMA,
        final_confidence=0.85,
        identified_red_flags=[],
        synthesized_explanation="Eczema"
    )
    decision = evaluator.evaluate(intake=intake, img_pred=img_pred, reasoning=reasoning)
    assert decision.action == ActionVerdict.RETAKE_IMAGE
    assert decision.abstain is True

def test_sanitize_dosages_and_prescriptions():
    tainted = "Take 500mg prednisone tablet twice daily."
    sanitized = sanitize_safety_constraints(tainted)
    assert "500mg" not in sanitized
    assert "prednisone" not in sanitized
    assert "twice daily" not in sanitized
