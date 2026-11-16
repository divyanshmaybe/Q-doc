"""Regression scenarios for consultation memory, safety and readiness."""
from services.dialogue.manager import DialogueManager
from services.dialogue.schemas import ClinicalIntakeSlots
from services.dialogue.consultation import ConsultationPlanner


class OfflineLLM:
    def generate_json(self, *args, **kwargs):
        return {"status": "fallback"}


def manager():
    return DialogueManager(llm_adapter=OfflineLLM())


def complete_slots(**overrides):
    values = dict(primary_language="en-IN", body_site="hands", duration_days=14,
                  has_itching=False, has_fever=False, has_pain=False, is_spreading=False,
                  safety_screen_complete=True, prior_treatments="none", patient_concern="cause",
                  daily_impact="none", photo_image_id="image1")
    values.update(overrides)
    return ClinicalIntakeSlots(**values)


def test_correction_and_raw_history_survive_serialization():
    dm = manager()
    slots, _, _, _ = dm.process_turn(ClinicalIntakeSlots(primary_language="en-IN"), "Rash on my hands for 3 days")
    slots = ClinicalIntakeSlots.model_validate_json(slots.model_dump_json())
    slots, _, _, _ = dm.process_turn(slots, "Actually, 3 weeks, no pain and not spreading")
    assert slots.duration_days == 21
    assert slots.has_pain is False
    assert slots.is_spreading is False
    assert len(slots.conversation_history) == 4
    assert any(f["previous"] == 3 and f["value"] == 21 for f in slots.fact_history)


def test_ambiguous_speech_is_not_a_negative_finding():
    slots, _, _, _ = manager().process_turn(ClinicalIntakeSlots(), "not achieved")
    assert slots.has_itching is None
    assert slots.planned_action == "clarify"


def test_treatment_request_cannot_bypass_missing_safety_checks():
    slots, _, ready, _ = manager().process_turn(ClinicalIntakeSlots(photo_image_id="p"), "Tell me treatment")
    assert not ready
    assert not slots.is_final_verdict_ready


def test_summary_requires_explicit_confirmation():
    planner = ConsultationPlanner(OfflineLLM())
    slots, _, _, _ = planner.step(complete_slots(), {"raw_transcript": "what is it?"}, [], "en")
    assert slots.planned_action == "summarize"
    slots, _, _, _ = planner.step(slots, {"raw_transcript": "yes"}, [], "en")
    assert slots.is_final_verdict_ready


def test_condition_question_answer_is_preserved_before_summary():
    planner = ConsultationPlanner(OfflineLLM())
    slots = complete_slots(primary_suspected_condition="urticaria")
    slots, message, _, _ = planner.step(slots, {"raw_transcript": "photo uploaded"}, [], "en")
    assert "one individual" in message
    assert slots.last_question_field == "condition_history:urticaria"
    slots, _, _, _ = planner.step(slots, {"raw_transcript": "each spot disappears after a few hours"}, [], "en")
    assert slots.condition_specific_history["urticaria"]["patient_response"] == "each spot disappears after a few hours"
    assert slots.condition_specific_history["urticaria"]["clinically_verified"] is False
    assert slots.planned_action == "summarize"


def test_every_named_condition_has_bilingual_history_prompt():
    from services.clinical_knowledge.coverage import CATALOG
    from services.clinical_knowledge.questions import QUESTIONS
    assert set(QUESTIONS) == set(CATALOG) - {"other_unclear", "possible_malignancy"}
    assert all(en and hi for en, hi in QUESTIONS.values())


def test_photo_upload_is_not_recorded_as_patient_condition_answer():
    slots = complete_slots(primary_suspected_condition="urticaria", last_question_field="condition_history:urticaria")
    slots, _, _, _ = ConsultationPlanner(OfflineLLM()).step(
        slots, {"raw_transcript": "", "event": "photo_uploaded"}, [], "en")
    assert "urticaria" not in slots.condition_specific_history
    assert slots.last_question_field == "condition_history:urticaria"


def test_emergency_preempts_photo_and_assessment():
    slots, msg, ready, _ = manager().process_turn(ClinicalIntakeSlots(primary_language="en-IN"), "I cannot breathe")
    assert slots.handoff_required and slots.handoff_urgency == "emergency"
    assert not ready and not slots.is_final_verdict_ready
    assert "emergency" in msg


def test_photo_declined_routes_to_examination():
    slots = complete_slots(photo_image_id=None, summary_confirmed=True, photo_declined=True)
    slots, _, _, _ = ConsultationPlanner(OfflineLLM()).step(slots, {"raw_transcript": "continue"}, [], "en")
    assert slots.planned_action == "handoff"


def test_vague_duration_remains_unknown():
    slots, _, _, _ = manager().process_turn(ClinicalIntakeSlots(), "A rash for a long time")
    assert slots.duration_days is None


def test_followup_does_not_restart_intake():
    slots = complete_slots(reviewed_plan="Arrange clinician review")
    slots, msg, _, _ = ConsultationPlanner(OfflineLLM()).step(slots, {"raw_transcript": "I cannot afford it"}, [], "en")
    assert slots.consultation_stage == "follow_up"
    assert "public clinic" in msg
    assert slots.treatment_barriers == "I cannot afford it"
