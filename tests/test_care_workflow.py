import pytest
from fastapi import HTTPException
from services.api import database
from services.api.routers.care import get_care, sign_care, record_follow_up, SignPlan, FollowUp


@pytest.fixture
def case(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "care.db"))
    monkeypatch.setenv("QDOC_CLINICIAN_KEY", "test-reviewer-secret")
    database.init_db()
    database.DatabaseRepo.create_session("test-session")
    database.DatabaseRepo.save_brief("test-session", {"clinical_reference": {"coverage": {"condition_id": "acne"}}})
    return "test-session"


def request(version):
    return SignPlan(evidence_version=version, reviewer_name="Test reviewer", registration_id="TEST-ONLY",
                    diagnosis="Provisional acne", instructions="Individualized test care instructions.",
                    follow_up="Review in the agreed interval", return_precautions="Seek help for worsening symptoms")


def test_signed_delivery_and_followup_invalidation(case):
    draft = get_care(case)
    assert draft["status"] == "draft" and draft["plan"] is None
    sign_care(case, request(draft["evidence_version"]), "Bearer test-reviewer-secret")
    signed = get_care(case)
    assert signed["status"] == "signed"
    assert signed["plan"]["instructions"] == "Individualized test care instructions."
    record_follow_up(case, FollowUp(progress="worse", notes="New symptoms", urgent_symptoms=True))
    updated = get_care(case)
    assert updated["status"] == "needs_review" and updated["plan"] is None
    assert updated["followups"][0]["urgent_symptoms"]
    with pytest.raises(HTTPException) as error:
        sign_care(case, request(draft["evidence_version"]), "Bearer test-reviewer-secret")
    assert error.value.status_code == 409


def test_signing_requires_server_credential(case, monkeypatch):
    req = request(get_care(case)["evidence_version"])
    with pytest.raises(HTTPException) as error:
        sign_care(case, req, "Bearer incorrect")
    assert error.value.status_code == 403
    monkeypatch.delenv("QDOC_CLINICIAN_KEY")
    with pytest.raises(HTTPException) as error:
        sign_care(case, req, None)
    assert error.value.status_code == 503


def test_new_patient_evidence_invalidates_plan(case):
    version = get_care(case)["evidence_version"]
    sign_care(case, request(version), "Bearer test-reviewer-secret")
    database.DatabaseRepo.log_turn(case, 0, "patient", "I have a new symptom", "{}")
    assert get_care(case)["status"] == "needs_review"


def test_unknown_session_has_no_plan(case):
    with pytest.raises(HTTPException) as error:
        get_care("not-a-session")
    assert error.value.status_code == 404


def test_basic_care_does_not_require_signature_but_requires_supported_screening(case):
    database.DatabaseRepo.save_brief(case, {
        "clinical_reference": {"coverage": {"management_scope": "basic_care_and_review", "basic_care": ["Gentle cleansing."]}},
        "triage_verdict": {"action": "speak_verdict", "abstain": False},
    })
    result = get_care(case)
    assert result["plan"] is None
    assert result["screening"]["basic_care"] == ["Gentle cleansing."]
    record_follow_up(case, FollowUp(progress="worse"))
    assert get_care(case)["screening"]["basic_care"] == []
