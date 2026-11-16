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
        reasoning: ClinicalReasonerOutput,
        mode: Optional[str] = None
    ) -> PolicyDecision:
        decision = self._evaluate(intake, img_pred, reasoning, mode)
        from services.clinical_knowledge.coverage import get_coverage
        if decision.urgency == UrgencyLevel.EMERGENCY:
            decision.screening_title = "Urgent screening finding"
        elif decision.action == ActionVerdict.RETAKE_IMAGE:
            decision.screening_title = "A clearer photo will help"
        elif decision.abstain:
            decision.screening_title = "Screening findings and next step"
        else:
            decision.screening_title = get_coverage(reasoning.top_diagnosis)["display_name"]
        return decision

    @staticmethod
    def _reported_findings(intake):
        """Summarize reported facts without inventing visual findings."""
        is_hi = "hi" in (intake.primary_language or "").lower()
        facts = []
        if intake.body_site:
            facts.append(f"स्थान: {intake.body_site}" if is_hi else f"location: {intake.body_site}")
        if intake.duration_days is not None:
            facts.append(f"अवधि: {intake.duration_days} दिन" if is_hi else f"duration: {intake.duration_days} days")
        if intake.has_itching is True:
            facts.append("खुजली" if is_hi else "itching")
        if intake.has_pain is True:
            facts.append("दर्द" if is_hi else "pain")
        if not facts:
            return ""
        return ("आपकी बताई जानकारी: " if is_hi else "You reported ") + ", ".join(facts) + ". "

    def _evaluate(
        self,
        intake: ClinicalIntakeSlots,
        img_pred: ImagePrediction,
        reasoning: ClinicalReasonerOutput,
        mode: Optional[str] = None
    ) -> PolicyDecision:
        self.reload_config()
        mode = mode or self.cfg["mode"]
        applied_rules = []
        is_hi = "hi" in (intake.primary_language or "").lower()

        # 2. Hard Red-Flags
        active_red_flags = [rf for rf in reasoning.identified_red_flags if rf in self.cfg["always_refer_red_flags"]]
        if intake.has_fever:
            active_red_flags.append("fever_with_rash")
        if reasoning.top_diagnosis in [SkinCondition.POSSIBLE_MALIGNANCY, "possible_malignancy"]:
            active_red_flags.append("possible_malignancy")

        from services.dialogue.consultation import intake_red_flags
        active_red_flags.extend(intake_red_flags(intake))

        # Deduplicate
        active_red_flags = sorted(list(set(active_red_flags)))

        if active_red_flags:
            applied_rules.extend(active_red_flags)
            is_emergency = ("fever_with_rash" in active_red_flags) or ("rapid_spread" in active_red_flags) or ("breathing_difficulty" in active_red_flags)
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

        # 1. Image Quality Check
        from services.clinical_knowledge.coverage import get_coverage
        coverage = get_coverage(reasoning.top_diagnosis)
        if coverage["management_scope"] == "refer" and coverage["condition_id"] != "other_unclear":
            msg = (
                "यह प्रारंभिक संभावना डॉक्टर की प्रत्यक्ष जांच मांगती है। कृपया डॉक्टर से संपर्क करें।"
                if is_hi else
                f"One provisional possibility is {coverage['display_name']}. "
                "This needs direct clinician assessment before condition-specific treatment."
            )
            if coverage["referral_priority"] == "prompt":
                msg += " कृपया जल्द जांच करवाएं।" if is_hi else " Please arrange prompt assessment."
            return PolicyDecision(
                action=ActionVerdict.REFER_ONLY, abstain=True,
                urgency=UrgencyLevel.SEEK_OPD, spoken_patient_message=msg,
                applied_rules=["CATALOG_REFERRAL_REQUIRED"],
            )

        if img_pred and img_pred.image_quality_score < self.cfg["thresholds"]["image_quality_min"]:
            msg = "फोटो साफ़ नहीं आई है। कृपया अच्छी रोशनी में दोबारा फोटो लें।" if is_hi else "The photo is blurry or dark. Please retake the photo in good lighting."
            return PolicyDecision(
                action=ActionVerdict.RETAKE_IMAGE,
                abstain=True,
                urgency=UrgencyLevel.ROUTINE,
                spoken_patient_message=msg,
                applied_rules=["IMAGE_QUALITY_FAIL"]
            )

        # 3. Confidence & Margin Checks (Abstention)
        margin = 0.0
        if len(reasoning.differential) >= 2:
            margin = reasoning.differential[0].probability - reasoning.differential[1].probability

        low_confidence = reasoning.final_confidence < self.cfg["thresholds"]["top1_confidence_min"]
        low_margin = margin < self.cfg["thresholds"]["top1_top2_margin_min"]

        is_unclear_class = coverage["condition_id"] == "other_unclear"
        is_extreme_uncertainty = (reasoning.final_confidence < 0.20)

        if is_unclear_class or is_extreme_uncertainty or low_confidence or low_margin:
            applied_rules.append("CONFIDENCE_ABSTENTION")
            if getattr(reasoning, "assessment_source", None) == "unavailable":
                msg = (
                    "डायग्नोस्टिक मॉडल वर्तमान में उपलब्ध नहीं है। कृपया त्वचा की प्रत्यक्ष जांच और सही देखभाल के लिए डॉक्टर से संपर्क करें।"
                    if is_hi else
                    "The diagnostic model is currently unavailable. Please arrange an in-person clinical examination to assess your skin and receive appropriate care."
                )
            else:
                msg = (
                    self._reported_findings(intake) +
                    "स्क्रीनिंग में अभी एक कारण चुनने के लिए पर्याप्त जानकारी नहीं है। "
                    "अगला कदम: चकत्ते के बदलाव और इस्तेमाल किए गए उत्पादों की जानकारी के साथ त्वचा की प्रत्यक्ष जांच। "
                    "इससे मिलते-जुलते कारणों में अंतर करके सही देखभाल चुनी जा सकती है।"
                    if is_hi else
                    self._reported_findings(intake) +
                    "Your screening needs one more step: the available information does not yet distinguish a single cause. "
                    "Next, an examination together with the rash timeline and products you have used can help separate similar conditions and select appropriate care."
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
                f"प्रारंभिक स्क्रीनिंग में {coverage['name_hi']} एक संभावना है; यह पक्का निदान नहीं है। "
                + self._reported_findings(intake) + "डॉक्टर देखभाल की योजना की समीक्षा करेंगे।"
                if is_hi else
                f"Your preliminary screening suggests {coverage['display_name']} as one possibility, not a confirmed diagnosis. "
                + self._reported_findings(intake) + "A doctor will review the care plan before it is finalized."
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
        # Patient-facing plans are constructed from approved structured content only.
        # No medication protocol is marked reviewed in the MVP, so medication advice
        # remains in the clinician brief rather than being generated for patients.
        diagnosis = getattr(reasoning.top_diagnosis, "value", str(reasoning.top_diagnosis)).replace("_", " ")
        sanitized_msg = (
            f"यह प्रारंभिक स्क्रीनिंग {diagnosis} की संभावना दिखाती है; यह पक्का निदान नहीं है। "
            "दवा का चुनाव आपके स्वास्थ्य की जानकारी और लक्षणों पर निर्भर करता है। लक्षण तेजी से बिगड़ें तो जल्द सहायता लें। "
            "आप अपने शब्दों में बताएंगे कि अगला कदम क्या है?"
            if is_hi else
            f"This screening suggests {diagnosis} as one possibility; it is not a confirmed diagnosis. "
            + ("Basic care: " + " ".join(coverage["basic_care"]) + " " if coverage["management_scope"] == "basic_care_and_review" and coverage["basic_care"] else "") +
            "Medication choices depend on your health history and the specific presentation. Seek prompt care if symptoms worsen quickly. "
            "Could you tell me in your own words what your next step will be?"
        )
        return PolicyDecision(
            action=ActionVerdict.SPEAK_VERDICT,
            abstain=False,
            urgency=UrgencyLevel.ROUTINE,
            spoken_patient_message=sanitized_msg,
            applied_rules=applied_rules
        )

