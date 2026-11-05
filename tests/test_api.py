from tests.test_api_v1 import (
    test_v1_session_and_dialogue,
    test_v1_photo_and_analysis_pipeline,
    test_v1_blurry_photo_rejection
)

def test_api_session_and_dialogue():
    test_v1_session_and_dialogue()

def test_api_photo_and_analysis():
    test_v1_photo_and_analysis_pipeline()

def test_api_blurry_rejection():
    test_v1_blurry_photo_rejection()
