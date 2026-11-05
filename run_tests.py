"""
Comprehensive Test Runner for Q-Doc MVP.
Runs:
1. Section 6 Directive Validation Checklist (Test Cases 1 - 5)
2. API v1 Routers & Pipeline Integration Tests
3. Stratified Evaluation Benchmarking
"""

import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("==================================================")
print("   Q-DOC MVP: OFFICIAL TEST SUITE EXECUTION       ")
print("==================================================")

try:
    print("\n[PART 1] Running Directive Validation Checklist (Section 6)...")
    from tests.test_directive_checklist import (
        test_case_1_scabies_catch,
        test_case_2_malignancy_policy_red_flag,
        test_case_3_fever_red_flag,
        test_case_4_mode_switch_verification,
        test_case_5_negative_guardrails
    )
    test_case_1_scabies_catch()
    test_case_2_malignancy_policy_red_flag()
    test_case_3_fever_red_flag()
    test_case_4_mode_switch_verification()
    test_case_5_negative_guardrails()
    print("--> All 5 Section 6 Validation Checklist tests PASSED!")

    print("\n[PART 2] Running API v1 Endpoint & Pipeline Tests...")
    from tests.test_api_v1 import (
        test_v1_session_and_dialogue,
        test_v1_photo_and_analysis_pipeline,
        test_v1_blurry_photo_rejection
    )
    test_v1_session_and_dialogue()
    print("[PASS] test_v1_session_and_dialogue passed!")
    test_v1_photo_and_analysis_pipeline()
    print("[PASS] test_v1_photo_and_analysis_pipeline passed!")
    test_v1_blurry_photo_rejection()
    print("[PASS] test_v1_blurry_photo_rejection passed!")
    print("--> All API v1 tests PASSED!")

    print("\n[PART 3] Running Held-out Stratified Benchmark Evaluation...")
    from eval.run_benchmarks import run_heldout_evaluation
    rep = run_heldout_evaluation()
    print(f"--> Benchmark passed! Total Cases: {rep['total_test_cases']}")
    print(f"    Multimodal Accuracy: {rep['multimodal_voice_and_image']['accuracy']}% (CI: {rep['multimodal_voice_and_image']['ci_95']})")
    print(f"    Gain from Voice History: {rep['gain_from_voice_history']['absolute_gain_pct']}")
    print(f"    Dangerous Malignancy Recall: {rep['dangerous_class_recall']['malignancy_recall_pct']}%")

    print("\n==================================================")
    print(" [SUCCESS] ALL Q-DOC MVP DIRECTIVE TESTS PASSED!  ")
    print("==================================================")

except Exception as e:
    import traceback
    print(f"\n[FAIL] Test suite failed: {e}")
    traceback.print_exc()
    sys.exit(1)
