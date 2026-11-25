"""Regression scenarios for consultation memory, safety and readiness."""
from services.dialogue.manager import DialogueManager
from services.dialogue.schemas import ClinicalIntakeSlots
from services.dialogue.consultation import ConsultationPlanner


class OfflineLLM:
    def generate_json(self, *args, **kwargs):
        return {"status": "fallback"}


def manager():
    return DialogueManager(llm_adapter=OfflineLLM())


def test_separate_safety_denials_open_photo_without_repeating_combined_screen():
    dm = manager()
    slots = ClinicalIntakeSlots(primary_language="hi-IN", body_site="पैर", duration_days=4,
                                has_fever=False, last_question_field="breathing_difficulty")
    slots, question, ready, _ = dm.process_turn(slots, "नहीं।")
    assert not ready and slots.safety_screen_complete is None
    assert slots.last_question_field == "mucosal_involvement" and "सांस" not in question
    slots = ClinicalIntakeSlots.model_validate_json(slots.model_dump_json())
    slots, _, ready, _ = dm.process_turn(slots, "नहीं।")
    assert ready and slots.safety_screen_complete is True


def test_unclear_spoken_age_requires_confirmation():
    class AgeGuess:
        def generate_json(self, *args):
            return {"age": 20}
    dm = DialogueManager(llm_adapter=AgeGuess())
    slots = ClinicalIntakeSlots(last_question_field="age")
    slots, question, *_ = dm.process_turn(slots, "बी साल।")
    assert slots.age is None and "20" in question
    slots, _, *_ = dm.process_turn(slots, "हाँ।")
    assert slots.age == 20 and slots.age_awaiting_confirmation is None


def test_age_in_years_does_not_overwrite_symptom_duration():
    class AgeAndDurationGuess:
        def generate_json(self, *args):
            return {"age": 20, "duration_days": 7300}

    for adapter in (OfflineLLM(), AgeAndDurationGuess()):
        dm = DialogueManager(llm_adapter=adapter)
        slots = ClinicalIntakeSlots(primary_language="hi-IN", duration_days=3, last_question_field="age")
        slots, *_ = dm.process_turn(slots, "खुजली मुझे ही हो रही है और मेरी उम्र 20 साल है।")
        assert slots.duration_days == 3

        slots.last_question_field = "age"
        slots, *_ = dm.process_turn(slots, "मेरी उम्र 20 साल है और खुजली 4 दिन से है।")
        assert slots.duration_days == 4


def test_all_extracted_fact_types_persist_and_can_be_corrected():
    from services.dialogue.schemas import IntakeFacts
    from services.gateway.llm import IntakeReply

    planner = ConsultationPlanner(OfflineLLM())
    properties = IntakeFacts.model_json_schema()["properties"]
    examples = {"boolean": (True, False), "integer": (3, 2), "string": ("first answer", "correction")}
    for field, definition in properties.items():
        kind = next(t["type"] for t in definition["anyOf"] if t["type"] != "null")
        slots = ClinicalIntakeSlots()
        for value in examples[kind]:
            reply = IntakeReply.model_validate({field: value}, strict=True)
            slots, *_ = planner.step(slots, reply.model_dump(exclude_unset=True), [], "en")
            slots = ClinicalIntakeSlots.model_validate_json(slots.model_dump_json())
            assert getattr(slots, field) == value, field
            assert field not in slots.missing_required_slots


def test_negative_night_itch_and_uncertain_household_answer_survive_restore():
    planner = ConsultationPlanner(OfflineLLM())
    slots = ClinicalIntakeSlots(has_itching=True, last_question_field="nocturnal_itch")
    slots, *_ = planner.step(slots, {"nocturnal_itch": False, "raw_transcript": "नहीं बढ़ती।"}, [], "hi")
    slots = ClinicalIntakeSlots.model_validate_json(slots.model_dump_json())
    assert slots.nocturnal_itch is False
    assert "nocturnal_itch" not in slots.missing_required_slots
    slots.last_question_field = "household_contacts_affected"
    slots, *_ = planner.step(slots, {"answer_unknown": True, "raw_transcript": "मुझे पता नहीं।"}, [], "hi")
    assert slots.household_contacts_affected is None
    assert "household_contacts_affected" not in slots.missing_required_slots
    assert slots.fact_status["household_contacts_affected"] == "patient_unsure"


def test_greeting_then_contextual_followup():
    class ContextLLM:
        def generate_json(self, system, prompt):
            assert "What’s been bothering you?" in prompt
            return {"has_itching": True, "next_field": "duration_days",
                    "next_question": "When did the nighttime itching start?"}

    dm = DialogueManager(llm_adapter=ContextLLM())
    slots, welcome, _, _ = dm.process_turn(ClinicalIntakeSlots(primary_language="en-IN"), "Hi!")
    assert welcome.startswith("Hi!")
    assert slots.last_question_field is None
    slots, question, _, _ = dm.process_turn(slots, "Hi doctor, my arms itch at night.")
    assert slots.has_itching
    assert slots.last_question_field == "duration_days"
    assert question == "When did the nighttime itching start?"


def complete_slots(**overrides):
    values = dict(primary_language="en-IN", body_site="hands", duration_days=14,
                  has_itching=False, has_fever=False, has_pain=False, is_spreading=False,
                  safety_screen_complete=True, prior_treatments="none", patient_concern="cause",
                  daily_impact="none", photo_image_id="image1")
    values.update(overrides)
    return ClinicalIntakeSlots(**values)


def test_revise_answered_topic_and_follow_patient_before_photo():
    class Revision:
        def generate_json(self, system, prompt):
            assert '"body_site": "arms"' in prompt
            return {"next_field": "daily_impact", "next_question": "क्या खुजली से आपकी नींद खुलती है?"}

    planner = ConsultationPlanner(Revision())
    slots = ClinicalIntakeSlots(body_site="arms")
    slots, question, *_ = planner.step(slots, {"raw_transcript": "रात को खुजली होती है",
        "next_field": "body_site", "next_question": "कहाँ?"}, [], "hi")
    assert slots.last_question_field == "daily_impact"
    assert "नींद" in question


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


def test_optional_topics_do_not_delay_recap_after_essential_history():
    planner = ConsultationPlanner(OfflineLLM())
    slots = complete_slots(has_itching=True, patient_concern=None, daily_impact=None,
                           pending_clarifications=["nocturnal_itch"])
    slots, recap, *_ = planner.step(
        slots, {"next_field": "daily_impact", "next_question": "Does it affect your sleep?"}, [], "en"
    )
    assert slots.consultation_stage == "summary"
    assert not slots.missing_required_slots
    assert "None" not in recap and "main concern" not in recap
    slots, *_ = planner.step(slots, {"raw_transcript": "yes"}, [], "en")
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

def test_live_intake_requires_current_turn_evidence(monkeypatch):
    from services.gateway.llm import LLMAdapter
    from services.dialogue.clinical_agent import UtteranceNormalizer

    adapter = LLMAdapter(api_key="test")
    reply = {"age": 20, "duration_days": 7300, "has_fever": True,
             "fact_evidence": {"age": "20 years", "duration_days": "20 years", "has_fever": "fever"}}
    monkeypatch.setattr(adapter, "generate_json", lambda *_: reply.copy())
    result = UtteranceNormalizer(adapter).normalize("I'm 20 years old")
    assert result["age"] == 20
    assert "duration_days" not in result and "has_fever" not in result
    reply.update(duration_days=3, fact_evidence={"age": "20 years", "duration_days": "three days"})
    result = UtteranceNormalizer(adapter).normalize("I'm 20 years old and it started three days ago")
    assert result["duration_days"] == 3
