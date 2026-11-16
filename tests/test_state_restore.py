from services.dialogue.schemas import ClinicalIntakeSlots
from services.dialogue.state import restore_intake


def test_newer_nulls_clear_old_plan_and_question():
    old = ClinicalIntakeSlots(reviewed_plan="Old plan", last_question_field="has_fever", primary_suspected_condition="acne")
    new = old.model_copy(update={"reviewed_plan": None, "last_question_field": None, "primary_suspected_condition": None})
    result = restore_intake([{"slots": old.model_dump()}, {"slots": new.model_dump()}], "en-IN")
    assert result.reviewed_plan is None
    assert result.last_question_field is None
    assert result.primary_suspected_condition is None


def test_partial_legacy_snapshot_and_false_values_survive():
    result = restore_intake([
        {"slots": {"body_site": "face", "has_fever": True, "duration_days": 7}},
        {"slots": {"has_fever": False, "duration_days": 0, "unknown_field": "ignored"}},
        {"slots": {}},
    ], "hi-IN")
    assert result.body_site == "face"
    assert result.has_fever is False
    assert result.duration_days == 0
    assert result.primary_language == "hi-IN"


def test_new_empty_collections_replace_old_values():
    result = restore_intake([
        {"slots": {"pending_clarifications": ["has_pain"], "suspected_differentials": ["acne"]}},
        {"slots": {"pending_clarifications": [], "suspected_differentials": []}},
    ], "en-IN")
    assert result.pending_clarifications == []
    assert result.suspected_differentials == []
