"""Software contract tests, not clinical diagnostic validation."""
import io
import json as jsonlib
from types import SimpleNamespace

import pytest
from PIL import Image

from services.clinical_knowledge.coverage import CATALOG, get_coverage, normalize_condition
from services.clinical_knowledge.dermatology_kb import DermatologyKnowledgeService
from services.dialogue.schemas import ClinicalIntakeSlots, ImagePrediction, SkinCondition
from services.policy.evaluator import PolicyEvaluator
from services.reasoner.multimodal_agent import MultimodalDermatologistAgent


@pytest.mark.parametrize("value,expected", [
    ("Shingles", "herpes_zoster"), ("tinea versicolor", "pityriasis_versicolor"),
    ("acne vulgaris", "acne"), ("not acne", "other_unclear"),
    ("", "other_unclear"), ("unlisted disorder", "other_unclear"),
    ("keratosis pilaris", "keratosis_pilaris"),
])
def test_exact_aliases(value, expected):
    assert normalize_condition(value) == expected


def test_catalog_and_knowledge_cover_all_records():
    assert len(CATALOG) == 32
    for key in CATALOG:
        record = get_coverage(key)
        assert record["content_status"] == "draft"
        assert record["treatment_summary"]
        assert DermatologyKnowledgeService.get_condition_info(key)["coverage"]["condition_id"] == key
    copied = get_coverage("rosacea")
    copied["basic_care"].append("changed")
    assert "changed" not in get_coverage("rosacea")["basic_care"]


@pytest.mark.parametrize("condition", ["rosacea", "herpes_zoster", "keratosis_pilaris", "unlisted disorder"])
def test_multimodal_catalog_roundtrip(monkeypatch, condition):
    agent = MultimodalDermatologistAgent(api_key="test-only")
    monkeypatch.setattr(agent.search_tool, "search_clinical_guidelines", lambda *a, **k: [])
    result_payload = {
        "primary_diagnosis": condition, "confidence": 0.8,
        "differential": [{"condition": condition, "probability": 0.8, "clinical_rationale": "test evidence"},
                         {"condition": "eczema", "probability": 0.1, "clinical_rationale": "alternative"}],
        "identified_red_flags": [],
        "spoken_patient_explanation": "MODEL_UNREVIEWED_TREATMENT",
        "first_line_management": {"otc_active_ingredients": ["MODEL_UNREVIEWED_TREATMENT"]},
    }

    def fake_post(url, json=None, **kwargs):
        prompt = json["contents"][0]["parts"][0]["text"]
        assert "keratosis_pilaris" in prompt and "pemphigus_vulgaris" in prompt
        assert "Fever: Unknown" in prompt
        return SimpleNamespace(status_code=200, json=lambda: {
            "candidates": [{"content": {"parts": [{"text": jsonlib.dumps(result_payload)}]}}]
        })

    monkeypatch.setattr("services.reasoner.multimodal_agent.requests.post", fake_post)
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), "white").save(buf, format="PNG")
    prediction = ImagePrediction(probabilities={SkinCondition.ECZEMA: 1.0},
                                 top_condition=SkinCondition.ECZEMA, confidence=0.9,
                                 image_quality_score=0.9, quality_passed=True)
    # Final score below classifier score previously crashed for non-enum diagnoses.
    result = agent.diagnose(buf.getvalue(), ClinicalIntakeSlots(primary_language="en-IN"), prediction)
    assert result.top_diagnosis == normalize_condition(condition)
    assert "MODEL_UNREVIEWED_TREATMENT" not in result.synthesized_explanation
    if condition in ("herpes_zoster", "unlisted disorder"):
        decision = PolicyEvaluator().evaluate(ClinicalIntakeSlots(primary_language="en-IN"), prediction, result, "autonomous")
        assert decision.action.value == "refer_only"
        expected_rule = "CATALOG_REFERRAL_REQUIRED" if condition == "herpes_zoster" else "CONFIDENCE_ABSTENTION"
        assert expected_rule in decision.applied_rules


def test_coverage_endpoint():
    from services.api.routers.analysis import list_condition_coverage
    result = list_condition_coverage()
    assert result["condition_count"] == 30
    assert result["special_category_count"] == 2
    assert len(result["classifier_labels"]) == 8
    assert "rosacea" not in result["classifier_labels"]
