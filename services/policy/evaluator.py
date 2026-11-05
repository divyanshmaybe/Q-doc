"""
Policy Evaluator for Q-Doc MVP.
Implements controllable autonomy, abstention checks, red-flags, and safety decisions.
"""

import os
import yaml
from typing import Optional
from services.dialogue.schemas import (
    SkinCondition,
    UrgencyLevel,
    ClinicalIntakeSlots,
    ImagePrediction,
    ClinicalReasonerOutput,
    ActionVerdict,
    PolicyDecision
)
from .rules import load_policy_config, DEFAULT_CONFIG_PATH, sanitize_safety_constraints

class PolicyEvaluator:
    def __init__(self, config_path: str = "config/policy.yaml"):
        # Resolve config path
        if not os.path.exists(config_path):
            config_path = DEFAULT_CONFIG_PATH
        self.config_path = config_path
        self.cfg = load_policy_config(config_path)

    def reload_config(self) -> None:
        self.cfg = load_policy_config(self.config_path)

    def evaluate(
        self,
        intake: ClinicalIntakeSlots,
        img_pred: ImagePrediction,
        reasoning: ClinicalReasonerOutput
    ) -> PolicyDecision:
        self.reload_config()
        mode = self.cfg["mode"]
        applied_rules = []
        is_hi = "hi" in (intake.primary_language or "").lower()

        # 1. Image Quality Check
        if img_pred.image_quality_score < self.cfg["thresholds"]["image_quality_min"]:
            msg = "फोटो साफ़ नहीं आई है। कृपया अच्छी रोशनी में दोबारा फोटो लें।" if is_hi else "The photo is blurry or dark. Please retake the photo in good lighting."
            return PolicyDecision(
                action=ActionVerdict.RETAKE_IMAGE,
                abstain=True,
                urgency=UrgencyLevel.ROUTINE,
                spoken_patient_message=msg,
                applied_rules=["IMAGE_QUALITY_FAIL"]
            )

        # 2. Hard Red-Flags
        active_red_flags = [rf for rf in reasoning.identified_red_flags if rf in self.cfg["always_refer_red_flags"]]
        if intake.has_fever:
            active_red_flags.append("fever_with_rash")
        if reasoning.top_diagnosis in [SkinCondition.POSSIBLE_MALIGNANCY, "possible_malignancy"]:
            active_red_flags.append("possible_malignancy")

        # Deduplicate
        active_red_flags = sorted(list(set(active_red_flags)))

        if active_red_flags:
            applied_rules.extend(active_red_flags)
            is_emergency = ("fever_with_rash" in active_red_flags) or ("rapid_spread" in active_red_flags)
            urgency = UrgencyLevel.EMERGENCY if is_emergency else UrgencyLevel.SEEK_OPD
            
            if "possible_malignancy" in active_red_flags:
                msg = (
                    "त्वचा पर दिख रहे इस निशान की प्रकृति की तुरंत किसी त्वचा विशेषज्ञ डॉक्टर से प्रत्यक्ष जांच करवानी चाहिए।"
                    if is_hi else
                    "This skin lesion requires direct professional examination by a dermatologist. Please schedule a consultation promptly."
                )
            else:
                msg = (
                    "आपके लक्षण डॉक्टर द्वारा सीधे जांच किए जाने आवश्यक हैं। कृपया जल्द से जल्द नजदीकी स्वास्थ्य केंद्र जाएं।"
                    if is_hi else
                    "Your symptoms indicate high-priority signs that require in-person medical evaluation. Please visit a clinic promptly."
                )

            return PolicyDecision(
                action=ActionVerdict.REFER_ONLY,
                abstain=True,
                urgency=urgency,
                spoken_patient_message=msg,
                applied_rules=applied_rules
            )

        # 3. Confidence & Margin Checks (Abstention)
        margin = 0.0
        if len(reasoning.differential) >= 2:
            margin = reasoning.differential[0].probability - reasoning.differential[1].probability

        low_confidence = reasoning.final_confidence < self.cfg["thresholds"]["top1_confidence_min"]
        low_margin = margin < self.cfg["thresholds"]["top1_top2_margin_min"]

        # Only abstain completely if it's truly unidentifiable without diagnosis OR extreme uncertainty (< 0.20)
        has_specific_diagnosis = any(term in reasoning.synthesized_explanation.lower() for term in [
            "acanthosis", "vitiligo", "melasma", "lichen planus", "dermatitis", "pityriasis", "alopecia", "rosacea", "urticaria", "scabies", "eczema", "psoriasis", "tinea", "acne"
        ])
        is_unclear_class = (reasoning.top_diagnosis in [SkinCondition.OTHER_UNCLEAR, "other_unclear"] and not has_specific_diagnosis)
        is_extreme_uncertainty = (reasoning.final_confidence < 0.20)

        if is_unclear_class or is_extreme_uncertainty:
            applied_rules.append("CONFIDENCE_ABSTENTION")
            msg = (
                "यह स्थिति पूरी तरह स्पष्ट नहीं है। सुरक्षित रहने के लिए डॉक्टर को दिखाना बेहतर होगा।"
                if is_hi else
                "The findings are non-conclusive. We recommend an evaluation by a healthcare provider."
            )
            return PolicyDecision(
                action=ActionVerdict.REFER_ONLY,
                abstain=True,
                urgency=UrgencyLevel.SEEK_OPD,
                spoken_patient_message=msg,
                applied_rules=applied_rules
            )

        # 4. Supervised vs Autonomous Mode Resolution
        if mode == "supervised":
            applied_rules.append("SUPERVISED_HOLD")
            msg = (
                "आपकी जानकारी दर्ज कर ली गई है। डॉक्टर इसकी समीक्षा कर रहे हैं।"
                if is_hi else
                "Your details have been recorded. A doctor will review your case shortly."
            )
            return PolicyDecision(
                action=ActionVerdict.SUPERVISED_QUEUE,
                abstain=False,
                urgency=UrgencyLevel.ROUTINE,
                spoken_patient_message=msg,
                applied_rules=applied_rules
            )

        # 5. Full Autonomous Verdict Spoken
        applied_rules.append("AUTONOMOUS_VERDICT_GRANTED")
        # Ensure negative guardrails on output
        sanitized_msg = sanitize_safety_constraints(reasoning.synthesized_explanation)
        return PolicyDecision(
            action=ActionVerdict.SPEAK_VERDICT,
            abstain=False,
            urgency=UrgencyLevel.ROUTINE,
            spoken_patient_message=sanitized_msg,
            applied_rules=applied_rules
        )

