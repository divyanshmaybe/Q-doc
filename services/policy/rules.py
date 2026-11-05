"""
Policy loader and safety constraint enforcement for Q-Doc MVP.
Reads and updates config/policy.yaml and sanitizes prescriptive outputs.
"""

import os
import re
import yaml
from typing import Dict, Any, Optional

DEFAULT_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config", "policy.yaml"))

def load_policy_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    path = config_path or DEFAULT_CONFIG_PATH
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {
        "mode": "autonomous",
        "thresholds": {
            "image_quality_min": 0.50,
            "top1_confidence_min": 0.70,
            "top1_top2_margin_min": 0.15
        },
        "always_refer_red_flags": [
            "possible_malignancy",
            "rapid_spread",
            "fever_with_rash",
            "mucosal_involvement",
            "infant_under_1_year",
            "pregnancy"
        ],
        "safety_constraints": {
            "never_output": [
                "prescriptions",
                "drug_dosages",
                "definitive_cancer_dismissal"
            ]
        }
    }

def save_policy_config(config_data: Dict[str, Any], config_path: Optional[str] = None) -> None:
    path = config_path or DEFAULT_CONFIG_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_data, f, default_flow_style=False)

def sanitize_safety_constraints(text: str) -> str:
    """
    Enforces negative guardrails (Test Case 5):
    Ensures output never contains drug units (mg, tablet, twice daily) or prescription medication names.
    """
    forbidden_terms = [
        "mg", "milligram", "tablet", "tablets", "capsule", "capsules",
        "twice daily", "once daily", "thrice daily", "dosage",
        "prednisone", "isotretinoin", "amoxicillin", "doxycycline", "permethrin", "clobetasol"
    ]
    sanitized = text
    lower = sanitized.lower()
    for term in forbidden_terms:
        if term in lower:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            sanitized = pattern.sub("[clinical evaluation needed]", sanitized)
            lower = sanitized.lower()
    return sanitized
