"""Restore encounter snapshots without resurrecting explicitly cleared values."""
from services.dialogue.schemas import ClinicalIntakeSlots


def restore_intake(turns, language):
    values = {}
    fields = ClinicalIntakeSlots.model_fields
    for turn in turns:
        snapshot = turn.get("slots")
        if isinstance(snapshot, dict):
            # Null is meaningful: a later snapshot can clear earlier state.
            values.update({key: value for key, value in snapshot.items() if key in fields})
    values["primary_language"] = language
    if "conversation_history" in values:
        values["conversation_history"] = [
            {"speaker": t["speaker"], "transcript": t["transcript"]}
            for t in values["conversation_history"] if isinstance(t, dict) and "speaker" in t and "transcript" in t
        ]
    return ClinicalIntakeSlots.model_validate(values)
