import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from services.api import database
from services.api.routers.patients import PatientEmail, link_patient, patient_history
from services.api.routers.care import FollowUp, record_follow_up


@pytest.fixture
def records(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "history.db"))
    database.init_db()
    for sid, diagnosis in (("visit-one", "acne"), ("visit-two", "eczema"), ("other-patient", "tinea")):
        database.DatabaseRepo.create_session(sid)
        database.DatabaseRepo.save_brief(sid, {"triage_verdict": {"top_diagnosis": diagnosis}})


def test_email_groups_visits_without_merging_diagnoses(records):
    first = link_patient("visit-one", " Patient@Example.com ")
    second = link_patient("visit-two", "patient@example.com")
    assert first["patient_id"] == second["patient_id"]
    link_patient("other-patient", "other@example.com")
    history = patient_history(PatientEmail(email="PATIENT@example.com"))
    assert len(history["encounters"]) == 2
    assert {v["screening"]["top_diagnosis"] for v in history["encounters"]} == {"acne", "eczema"}


def test_followup_belongs_to_specific_visit(records):
    link_patient("visit-one", "patient@example.com")
    link_patient("visit-two", "patient@example.com")
    record_follow_up("visit-one", FollowUp(progress="better", notes="Less itching"))
    visits = {v["session_id"]: v for v in patient_history(PatientEmail(email="patient@example.com"))["encounters"]}
    assert visits["visit-one"]["followups"][0]["notes"] == "Less itching"
    assert visits["visit-two"]["followups"] == []


def test_idempotent_link_and_reassignment_rejected(records):
    first = link_patient("visit-one", "patient@example.com")
    assert link_patient("visit-one", "patient@example.com") == first
    with pytest.raises(HTTPException) as error:
        link_patient("visit-one", "someoneelse@example.com")
    assert error.value.status_code == 409


def test_unknown_email_and_bad_input(records):
    assert patient_history(PatientEmail(email="new@example.com"))["encounters"] == []
    with pytest.raises(ValidationError):
        PatientEmail(email="not an email")
    with pytest.raises(HTTPException) as error:
        link_patient("missing", "patient@example.com")
    assert error.value.status_code == 404


def test_session_start_links_email_and_uses_full_visit_id(records, monkeypatch):
    import uuid
    from services.api.routers import session
    monkeypatch.setattr(session, "_get_cached_welcome_audio", lambda *a: {})
    created = session.start_session(session.StartSessionRequest(email=" Person@Example.com "))
    assert str(uuid.UUID(created["session_id"])) == created["session_id"]
    assert created["patient"]["email"] == "person@example.com"
    assert patient_history(PatientEmail(email="person@example.com"))["encounters"][0]["session_id"] == created["session_id"]


def test_invalid_start_metadata_is_rejected():
    from services.api.routers.session import StartSessionRequest
    for payload in ({"mode": "invalid"}, {"age": -1}, {"age": 150}):
        with pytest.raises(ValidationError):
            StartSessionRequest(**payload)
