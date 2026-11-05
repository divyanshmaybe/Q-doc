"""
Unit and integration tests for Q-Doc MVP API v1 Endpoints.
Tests session start, turn processing, photo upload, analyze, clinician brief, and mode toggling.
"""

import os
import sys
import io
from PIL import Image
from fastapi import UploadFile

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.api.routers import session, intake, analysis, brief
from services.policy.rules import load_policy_config, save_policy_config

def test_v1_session_and_dialogue():
    # 1. Start Session in Hindi
    start_req = session.StartSessionRequest(language="hi-IN", mode="autonomous")
    sess_res = session.start_session(start_req)
    session_id = sess_res["session_id"]
    assert session_id is not None
    assert sess_res["language"] == "hi-IN"
    assert "नमस्ते" in sess_res["agent_message"]

    # 2. Process Turn
    turn_req = intake.TextTurnRequest(
        transcript="मेरे हाथ और उंगलियों के बीच दो हफ्ते से बहुत खुजली हो रही है",
        language="hi-IN"
    )
    turn_res = intake.process_intake_turn(session_id, turn_req)
    assert turn_res["session_id"] == session_id
    assert turn_res["slots"]["body_site"] == "hands"
    assert turn_res["slots"]["duration_days"] == 14
    assert turn_res["slots"]["has_itching"] is True

    # 3. Test Admin Mode Toggle
    mode_res = session.set_admin_mode(session.ModeToggleRequest(mode="supervised"))
    assert mode_res["success"] is True
    assert mode_res["mode"] == "supervised"

    # Reset back to autonomous
    session.set_admin_mode(session.ModeToggleRequest(mode="autonomous"))

def test_v1_photo_and_analysis_pipeline():
    # 1. Start session
    start_req = session.StartSessionRequest(language="en-IN", mode="autonomous")
    sess_res = session.start_session(start_req)
    session_id = sess_res["session_id"]

    # 2. Feed Scabies history (Test Case 1 conditions)
    turn_req = intake.TextTurnRequest(
        transcript="Rash on wrists and web spaces of fingers for 14 days, severe night itching, brother scratching all night too.",
        language="en-IN"
    )
    intake.process_intake_turn(session_id, turn_req)

    # 3. Create synthetic test image with texture (to pass blur quality check)
    import numpy as np
    arr = np.random.RandomState(42).randint(60, 210, (300, 300, 3), dtype=np.uint8)
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    upload_file = UploadFile(
        file=buf,
        filename="lesion_photo.jpg",
        headers={"content-type": "image/jpeg"}
    )

    # Upload Photo
    photo_res = analysis.upload_photo(session_id, upload_file)
    assert "image_id" in photo_res
    image_id = photo_res["image_id"]

    # 4. Run Analyze
    analysis_res = analysis.analyze_session(session_id, image_id=image_id)
    assert analysis_res["session_id"] == session_id
    assert "image_prediction" in analysis_res
    assert "reasoner_output" in analysis_res
    assert "policy_decision" in analysis_res
    assert analysis_res["reasoner_output"]["top_diagnosis"] == "scabies"
    assert analysis_res["policy_decision"]["action"] in ["speak_verdict", "refer_only", "supervised_queue"]

    # 5. Retrieve Clinician Brief
    brief_data = brief.get_clinician_brief(session_id)
    assert brief_data is not None
    assert "chief_complaint_and_timeline" in brief_data["brief_data"]
    assert "triage_verdict" in brief_data["brief_data"]

    # 6. Clinician One-Click Approval Sign-off
    review_res = brief.review_clinician_brief(
        session_id,
        brief.DoctorReviewRequest(approved=True, notes="Verified concordance with scabies triad.")
    )
    assert review_res["success"] is True

def test_v1_blurry_photo_rejection():
    # Test quality rejection on blurry photo
    sess_res = session.start_session(session.StartSessionRequest(language="en-IN"))
    session_id = sess_res["session_id"]

    # Flat uniform color with zero edges gives Laplacian variance 0.0 (< 100)
    flat_img = Image.new("RGB", (200, 200), color=(50, 50, 50))
    buf = io.BytesIO()
    flat_img.save(buf, format="JPEG")
    buf.seek(0)

    upload_file = UploadFile(
        file=buf,
        filename="blurry.jpg",
        headers={"content-type": "image/jpeg"}
    )
    photo_res = analysis.upload_photo(session_id, upload_file)
    assert photo_res["quality_passed"] is False
    assert photo_res["action"] == "retake_image"
    print("\n[PASS] test_v1_blurry_photo_rejection PASSED! Rejection action:", photo_res["action"])

if __name__ == "__main__":
    test_v1_session_and_dialogue()
    print("[PASS] test_v1_session_and_dialogue PASSED!")
    test_v1_photo_and_analysis_pipeline()
    print("[PASS] test_v1_photo_and_analysis_pipeline PASSED!")
    test_v1_blurry_photo_rejection()
    print("\n[SUCCESS] ALL API V1 TESTS PASSED!")
