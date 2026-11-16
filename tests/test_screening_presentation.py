"""Presentation should be useful without disguising uncertainty or urgency."""
import pytest

from services.dialogue.schemas import (
    ClinicalIntakeSlots, ClinicalReasonerOutput, DifferentialDiagnosisItem,
    ImagePrediction, SkinCondition,
)
from services.policy.evaluator import PolicyEvaluator


def evaluate(condition="acne", score=0.9, mode="supervised", **facts):
    intake = ClinicalIntakeSlots(primary_language="en-IN", body_site="face", duration_days=7, **facts)
    prediction = ImagePrediction(probabilities={SkinCondition.ACNE: 0.9}, top_condition=SkinCondition.ACNE,
                                 confidence=0.9, image_quality_score=0.9, quality_passed=True)
    reasoning = ClinicalReasonerOutput(
        top_diagnosis=condition, final_confidence=score,
        differential=[DifferentialDiagnosisItem(condition=condition, probability=score, clinical_justification="test"),
                      DifferentialDiagnosisItem(condition="eczema", probability=0.05, clinical_justification="alternative")],
        identified_red_flags=[], synthesized_explanation="Acne appears in this untrusted explanation.",
    )
    return PolicyEvaluator().evaluate(intake, prediction, reasoning, mode)


def test_supervised_result_contains_screening_not_just_queue():
    decision = evaluate()
    assert decision.action.value == "supervised_queue"
    assert decision.screening_title == "Acne Vulgaris"
    assert "face" in decision.spoken_patient_message
    assert "7 days" in decision.spoken_patient_message
    assert "not a confirmed diagnosis" in decision.spoken_patient_message
    assert "care plan" in decision.spoken_patient_message


@pytest.mark.parametrize("condition,score", [("other_unclear", 0.9), ("acne", 0.1), ("unknown_condition", 0.9)])
def test_uncertain_result_is_useful_without_forced_label(condition, score):
    decision = evaluate(condition, score)
    assert decision.abstain
    assert decision.action.value == "refer_only"
    assert "next step" in decision.screening_title.lower()
    assert "other_unclear" not in decision.spoken_patient_message
    assert "does not yet distinguish" in decision.spoken_patient_message
    assert "face" in decision.spoken_patient_message
    assert "Acne" not in decision.screening_title


def test_urgent_action_survives_presentation_changes():
    decision = evaluate(breathing_difficulty=True)
    assert decision.action.value == "refer_only"
    assert decision.urgency.value == "emergency"
    assert decision.screening_title == "Urgent screening finding"


def test_referral_only_condition_still_names_provisional_possibility():
    decision = evaluate("herpes_zoster")
    assert decision.action.value == "refer_only"
    assert "provisional possibility" in decision.spoken_patient_message
    assert "prompt assessment" in decision.spoken_patient_message
