from services.dialogue.manager import DialogueManager
from services.dialogue.schemas import ClinicalIntakeSlots
from services.reasoner.multimodal_agent import MultimodalDermatologistAgent


class OfflineLLM:
    def generate_json(self, *args, **kwargs):
        return {"status": "fallback"}


def test_positive_symptom_survives_different_symptom_denial():
    manager = DialogueManager(llm_adapter=OfflineLLM())
    slots, _, _, _ = manager.process_turn(ClinicalIntakeSlots(primary_language="en-IN"),
                                        "No mouth sores, but my skin peeling is getting worse")
    assert slots.mucosal_involvement is True
    assert slots.handoff_required


def test_multiple_negative_symptoms_do_not_create_positive():
    manager = DialogueManager(llm_adapter=OfflineLLM())
    slots, _, _, _ = manager.process_turn(ClinicalIntakeSlots(primary_language="en-IN"),
                                        "No mouth sores and no skin peeling")
    assert slots.mucosal_involvement is not True


def test_failed_vision_does_not_invent_neck_findings_for_arm():
    agent = MultimodalDermatologistAgent(api_key="test")
    agent.gemini_key = ""
    result = agent.inspect_early_photo(b"not-an-image", ClinicalIntakeSlots(body_site="arm"), "en")
    assert result["vision_available"] is False
    assert result["visual_morphology"] is None
    assert result["candidate_differentials"] == []
    assert result["initial_confidence"] == 0
    assert "examined" not in result["agent_question"]
    assert "neck" not in result["agent_question"]


def test_model_unavailable_when_key_missing_does_not_guess_bayesian():
    from services.policy.evaluator import PolicyEvaluator
    agent = MultimodalDermatologistAgent(api_key="test")
    agent.gemini_key = ""
    result = agent.diagnose(b"not-an-image", ClinicalIntakeSlots(body_site="hands", has_itching=True, household_contacts_affected=True), language="en")
    assert result.assessment_source == "unavailable"
    assert result.top_diagnosis == "other_unclear"
    assert result.final_confidence == 0.0
    assert result.differential == []
    assert "unavailable" in result.synthesized_explanation.lower()

    decision = PolicyEvaluator().evaluate(ClinicalIntakeSlots(primary_language="en-IN"), None, result, "autonomous")
    assert decision.action.value == "refer_only"
    assert decision.abstain is True
    assert "unavailable" in decision.spoken_patient_message.lower()
from services.dialogue.clinical_agent import UtteranceNormalizer
from services.dialogue.consultation import FACTS


class ConfusedLLM:
    def generate_json(self, *args, **kwargs):
        return {"ambiguous_fields": list(FACTS)}


def test_unmentioned_fields_are_not_ambiguous():
    result = UtteranceNormalizer(ConfusedLLM()).normalize("on thighs")
    assert result["ambiguous_fields"] == []


def test_real_session_no_answers_advance_without_clarification_loop():
    dm = DialogueManager(llm_adapter=ConfusedLLM())
    slots = ClinicalIntakeSlots(primary_language="en-IN")
    for text in ("i am having itching on my legs on thighs", "last 5 days ago", "no", "no"):
        slots, msg, _, _ = dm.process_turn(slots, text)
    assert slots.body_site == "legs"
    assert slots.duration_days == 5
    assert slots.has_itching is True
    assert slots.has_fever is False
    assert slots.safety_screen_complete is True
    assert slots.is_ready_for_photo
    assert "has_pain" in slots.missing_required_slots
    assert slots.pending_clarifications == []


def test_existing_corrupted_session_recovers_without_erasing_history():
    dm = DialogueManager(llm_adapter=ConfusedLLM())
    slots = ClinicalIntakeSlots(primary_language="en-IN", photo_declined=True, body_site="legs", duration_days=5,
        has_itching=True, has_fever=False, safety_screen_complete=True,
        last_question_field="lesion_type", pending_clarifications=list(FACTS)[:15])
    slots, msg, _, _ = dm.process_turn(slots, "on thigh near pubic area")
    assert slots.body_site == "groin"
    assert slots.duration_days == 5
    assert slots.has_fever is False
    assert slots.last_question_field == "has_pain"
    assert not slots.pending_clarifications


def test_evidenced_uncertainty_is_still_clarified():
    class UncertainLLM:
        def generate_json(self, *args, **kwargs):
            return {"ambiguous_fields": ["duration_days"],
                    "ambiguity_evidence": {"duration_days": "days or weeks"}}
    dm = DialogueManager(llm_adapter=UncertainLLM())
    slots, _, _, _ = dm.process_turn(ClinicalIntakeSlots(body_site="legs"), "days or weeks, I am unsure")
    assert slots.planned_action == "clarify"
    assert slots.last_question_field == "duration_days"


def test_itching_answer_does_not_invalidate_location_or_deny_pain():
    class MisinterpretingLLM:
        def generate_json(self, *args, **kwargs):
            return {"has_itching": True, "has_pain": False,
                    "ambiguous_fields": ["body_site"],
                    "ambiguity_evidence": {"body_site": "it"}}
    dm = DialogueManager(llm_adapter=MisinterpretingLLM())
    slots = ClinicalIntakeSlots(primary_language="en-IN", photo_declined=True, body_site="legs", duration_days=5,
        has_fever=False, has_itching=True, safety_screen_complete=True, last_question_field="has_pain")
    slots, msg, _, _ = dm.process_turn(slots, "it itches")
    assert slots.body_site == "legs"
    assert slots.has_pain is None
    assert slots.pending_clarifications == []
    assert slots.last_question_field == "has_pain"


def test_spurious_known_location_clarification_can_recover():
    dm = DialogueManager(llm_adapter=OfflineLLM())
    slots = ClinicalIntakeSlots(primary_language="en-IN", photo_declined=True, body_site="legs", duration_days=5,
        has_fever=False, has_itching=True, safety_screen_complete=True,
        pending_clarifications=["body_site"], last_question_field="body_site")
    slots, _, _, _ = dm.process_turn(slots, "it itches")
    assert slots.last_question_field == "has_pain"
    assert not slots.pending_clarifications


def test_previous_inferred_no_pain_is_repaired_from_provenance():
    dm = DialogueManager(llm_adapter=OfflineLLM())
    slots = ClinicalIntakeSlots(primary_language="en-IN", photo_declined=True, body_site="legs", duration_days=5,
        has_fever=False, has_itching=True, has_pain=False, safety_screen_complete=True,
        pending_clarifications=["body_site"], last_question_field="body_site",
        fact_history=[{"field": "has_pain", "value": False, "previous": None, "transcript": "it itches"}])
    slots, msg, _, _ = dm.process_turn(slots, "on thighs")
    assert slots.has_pain is None
    assert slots.last_question_field == "has_pain"
    assert not slots.pending_clarifications
