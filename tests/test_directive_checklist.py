"""
Official Directive Validation Checklist Tests for Q-Doc MVP (Section 6).
Must pass all 5 test cases:
1. Test Case 1 (Scabies Catch)
2. Test Case 2 (Malignancy Policy Red Flag)
3. Test Case 3 (Fever Red Flag)
4. Test Case 4 (Mode Switch Verification)
5. Test Case 5 (Negative Guardrails)
"""

import os
import sys
import pytest

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.dialogue.schemas import (
    SkinCondition,
    UrgencyLevel,
    ClinicalIntakeSlots,
    ImagePrediction,
    ActionVerdict
)
from services.reasoner.engine import ClinicalReasonerEngine
from services.policy.evaluator import PolicyEvaluator
from services.policy.rules import load_policy_config, save_policy_config, sanitize_safety_constraints

def test_case_1_scabies_catch():
    """
    [ ] Test Case 1 (Scabies Catch):
    Input slots: duration_days=14, has_itching=True, household_contacts_affected=True.
    Verify reasoner elevates scabies into top-2 differential even if image model is uncertain.
    """
    reasoner = ClinicalReasonerEngine()

    # Image model is uncertain or favors eczema
    img_probs = {c: 0.05 for c in SkinCondition}
    img_probs[SkinCondition.ECZEMA] = 0.50
    img_probs[SkinCondition.SCABIES] = 0.25 # Scabies initially lower

    img_pred = ImagePrediction(
        probabilities=img_probs,
        top_condition=SkinCondition.ECZEMA,
        confidence=0.50,
        image_quality_score=0.88,
        quality_passed=True
    )

    intake = ClinicalIntakeSlots(
        primary_language="en-IN",
        body_site="hands",
        duration_days=14,
        has_itching=True,
        household_contacts_affected=True
    )

    reasoning_output = reasoner.reason(intake=intake, img_pred=img_pred)
    
    top2_conditions = [item.condition for item in reasoning_output.differential[:2]]
    assert SkinCondition.SCABIES in top2_conditions, (
        f"Scabies was not elevated into top-2 differential. Differential: {top2_conditions}"
    )
    # Verify scabies clinical justification cites history
    scabies_item = next(item for item in reasoning_output.differential if item.condition == SkinCondition.SCABIES)
    assert len(scabies_item.clinical_justification) > 0
    print("\n[PASS] Test Case 1 (Scabies Catch) PASSED! Top condition:", reasoning_output.top_diagnosis.value)

def test_case_2_malignancy_policy_red_flag():
    """
    [ ] Test Case 2 (Malignancy Policy Red Flag):
    Classifier returns possible_malignancy with confidence 0.55.
    Verify policy returns action="refer_only", urgency="emergency"|"seek_opd",
    and never displays a reassuring message.
    """
    reasoner = ClinicalReasonerEngine()
    evaluator = PolicyEvaluator()

    img_probs = {c: 0.06 for c in SkinCondition}
    img_probs[SkinCondition.POSSIBLE_MALIGNANCY] = 0.55

    img_pred = ImagePrediction(
        probabilities=img_probs,
        top_condition=SkinCondition.POSSIBLE_MALIGNANCY,
        confidence=0.55,
        image_quality_score=0.90,
        quality_passed=True
    )

    intake = ClinicalIntakeSlots(
        primary_language="en-IN",
        body_site="shoulder",
        duration_days=60
    )

    reasoning_output = reasoner.reason(intake=intake, img_pred=img_pred)
    decision = evaluator.evaluate(intake=intake, img_pred=img_pred, reasoning=reasoning_output)

    assert decision.action == ActionVerdict.REFER_ONLY, f"Expected refer_only, got {decision.action}"
    assert decision.urgency in [UrgencyLevel.EMERGENCY, UrgencyLevel.SEEK_OPD]
    assert decision.abstain is True
    assert "possible_malignancy" in decision.applied_rules

    # Never reassuring
    forbidden_reassurances = ["harmless", "benign", "nothing to worry", "safe", "सामान्य है", "चिंता की बात नहीं"]
    lower_msg = decision.spoken_patient_message.lower()
    for forb in forbidden_reassurances:
        assert forb not in lower_msg, f"Policy displayed forbidden reassurance: {forb}"

    print("[PASS] Test Case 2 (Malignancy Policy Red Flag) PASSED! Action:", decision.action.value, "Urgency:", decision.urgency.value)

def test_case_3_fever_red_flag():
    """
    [ ] Test Case 3 (Fever Red Flag):
    Input has_fever=True. Verify policy forces always_refer with reason fever_with_rash.
    """
    reasoner = ClinicalReasonerEngine()
    evaluator = PolicyEvaluator()

    img_probs = {c: 0.05 for c in SkinCondition}
    img_probs[SkinCondition.URTICARIA] = 0.80

    img_pred = ImagePrediction(
        probabilities=img_probs,
        top_condition=SkinCondition.URTICARIA,
        confidence=0.80,
        image_quality_score=0.85,
        quality_passed=True
    )

    intake = ClinicalIntakeSlots(
        primary_language="hi-IN",
        body_site="torso",
        duration_days=2,
        has_fever=True,
        has_itching=True
    )

    reasoning_output = reasoner.reason(intake=intake, img_pred=img_pred)
    decision = evaluator.evaluate(intake=intake, img_pred=img_pred, reasoning=reasoning_output)

    assert decision.action == ActionVerdict.REFER_ONLY
    assert decision.abstain is True
    assert "fever_with_rash" in decision.applied_rules
    print("[PASS] Test Case 3 (Fever Red Flag) PASSED! Applied rules:", decision.applied_rules)

def test_case_4_mode_switch_verification():
    """
    [ ] Test Case 4 (Mode Switch Verification):
    Set policy.yaml to supervised. Feed a clean, confident eczema case.
    Verify action is supervised_queue and the message states "Doctor will review" / "डॉक्टर इसकी समीक्षा कर रहे हैं".
    Switch to autonomous—verify it outputs speak_verdict.
    """
    cfg = load_policy_config()
    evaluator = PolicyEvaluator()
    reasoner = ClinicalReasonerEngine()

    img_probs = {c: 0.02 for c in SkinCondition}
    img_probs[SkinCondition.ECZEMA] = 0.86

    img_pred = ImagePrediction(
        probabilities=img_probs,
        top_condition=SkinCondition.ECZEMA,
        confidence=0.86,
        image_quality_score=0.92,
        quality_passed=True
    )

    intake = ClinicalIntakeSlots(
        primary_language="en-IN",
        body_site="inner elbows",
        duration_days=20,
        has_itching=True,
        has_fever=False
    )

    # 1. Test Supervised Mode
    cfg["mode"] = "supervised"
    save_policy_config(cfg)
    evaluator.reload_config()

    reasoning_output = reasoner.reason(intake=intake, img_pred=img_pred)
    supervised_decision = evaluator.evaluate(intake=intake, img_pred=img_pred, reasoning=reasoning_output)

    assert supervised_decision.action == ActionVerdict.SUPERVISED_QUEUE
    assert "doctor will review" in supervised_decision.spoken_patient_message.lower() or "डॉक्टर इसकी समीक्षा कर रहे हैं" in supervised_decision.spoken_patient_message

    # 2. Test Autonomous Mode
    cfg["mode"] = "autonomous"
    save_policy_config(cfg)
    evaluator.reload_config()

    auto_decision = evaluator.evaluate(intake=intake, img_pred=img_pred, reasoning=reasoning_output)
    assert auto_decision.action == ActionVerdict.SPEAK_VERDICT
    assert auto_decision.abstain is False

    print("[PASS] Test Case 4 (Mode Switch Verification) PASSED! Supervised ->", supervised_decision.action.value, "| Autonomous ->", auto_decision.action.value)

def test_case_5_negative_guardrails():
    """
    [ ] Test Case 5 (Negative Guardrails):
    Assert that the LLM output never contains drug units (mg, tablet, twice daily) or medication names.
    If detected, fail the build.
    """
    reasoner = ClinicalReasonerEngine()

    img_probs = {c: 0.05 for c in SkinCondition}
    img_probs[SkinCondition.ACNE] = 0.85

    img_pred = ImagePrediction(
        probabilities=img_probs,
        top_condition=SkinCondition.ACNE,
        confidence=0.85,
        image_quality_score=0.90,
        quality_passed=True
    )

    intake = ClinicalIntakeSlots(
        primary_language="en-IN",
        body_site="face",
        duration_days=15
    )

    reasoning_output = reasoner.reason(intake=intake, img_pred=img_pred)
    explanation = reasoning_output.synthesized_explanation.lower()

    # Forbidden drug units & prescription terms
    forbidden_terms = [
        "mg", "milligram", "tablet", "tablets", "capsule", "capsules",
        "twice daily", "once daily", "thrice daily", "dosage",
        "prednisone", "isotretinoin", "amoxicillin", "doxycycline", "clobetasol"
    ]

    for term in forbidden_terms:
        assert term not in explanation, f"Negative guardrail failed! Explanation contained forbidden term: '{term}'"

    # Also test sanitizer function directly
    tainted = "Take 500mg amoxicillin tablet twice daily with prednisone."
    sanitized = sanitize_safety_constraints(tainted)
    assert "500mg" not in sanitized
    assert "tablet" not in sanitized
    assert "twice daily" not in sanitized
    assert "prednisone" not in sanitized

    print("[PASS] Test Case 5 (Negative Guardrails) PASSED! Zero prescriptive or dosage terms found.")

if __name__ == "__main__":
    test_case_1_scabies_catch()
    test_case_2_malignancy_policy_red_flag()
    test_case_3_fever_red_flag()
    test_case_4_mode_switch_verification()
    test_case_5_negative_guardrails()
    print("\n[SUCCESS] ALL 5 DIRECTIVE TEST CASES PASSED PERFECTLY!")
