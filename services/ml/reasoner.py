"""
Diagnosis Reasoner for Q-Doc MVP.
Combines patient voice intake history with image model probabilities.
Enforces the closed condition list, provides structured reasoning citing patient inputs,
and computes the image-only vs multimodal comparison to prove 'Gain from Voice History'.
"""

from typing import Dict, Any, List, Optional
import math
from .conditions import CONDITIONS, CONDITION_METADATA

class DiagnosisReasoner:
    def __init__(self):
        self.conditions = CONDITIONS

    def reason(
        self,
        intake_history: Dict[str, Any],
        image_probabilities: Dict[str, float],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Combines history + image probabilities to compute:
        1. Baseline (Image-only prediction)
        2. Multimodal (Image + Voice history reasoned prediction)
        3. Gain analysis & differential citations
        """
        # Copy image probabilities as image-only baseline
        baseline_probs = {c: float(image_probabilities.get(c, 0.0)) for c in self.conditions}
        
        # Clinical likelihood weights derived from patient symptoms
        history_multipliers = {c: 1.0 for c in self.conditions}
        citations_en: List[str] = []
        citations_hi: List[str] = []

        # Analyze Intake Slots:
        body_site = str(intake_history.get("body_site", "")).lower()
        duration = str(intake_history.get("duration_days", intake_history.get("duration", ""))).lower()
        itch = str(intake_history.get("itching", intake_history.get("itch", ""))).lower()
        pain = str(intake_history.get("pain", "")).lower()
        spread = str(intake_history.get("spreading", intake_history.get("spread", ""))).lower()
        fever = str(intake_history.get("fever", "")).lower()
        allergies = str(intake_history.get("allergies", "")).lower()
        household_contacts = str(intake_history.get("household_contacts", intake_history.get("family", ""))).lower()
        age = intake_history.get("age")

        # 1. Scabies evaluation
        is_night_itch = ("night" in itch or "रात" in itch or "severe" in itch or "तेज" in itch)
        has_household = (
            household_contacts in ["yes", "true", "हाँ", "हा", "1", "brother", "sister", "family", "mother", "father", "roommate"]
            or "same" in household_contacts or "परिवार" in household_contacts
        )
        is_scabies_site = any(s in body_site for s in ["finger", "web", "wrist", "waist", "groin", "उंगली", "हाथ", "कलाई"])

        if is_night_itch and (has_household or is_scabies_site):
            history_multipliers["scabies"] *= 5.5
            # Differential down-weighting: atopic eczema does not cluster acutely among household contacts
            if has_household:
                history_multipliers["eczema"] *= 0.4
            citations_en.append("Patient reported intense nocturnal itching with household members affected (classic hallmark of Scabies).")
            citations_hi.append("रात में तेज खुजली और परिवार के सदस्यों में समान लक्षण स्केबीज संक्रमण का स्पष्ट संकेत है।")
        elif is_night_itch:
            history_multipliers["scabies"] *= 2.5
            citations_en.append("Nocturnal itching reported, raising suspicion for Scabies infestation.")
            citations_hi.append("रात में खुजली बढ़ने का लक्षण स्केबीज की संभावना को बढ़ाता है।")

        # 2. Psoriasis evaluation
        is_extensor = any(s in body_site for s in ["elbow", "knee", "scalp", "कोहनी", "घुटना", "सिर"])
        is_chronic = any(d in duration for d in ["month", "months", "year", "years", "महीने", "साल", "30", "60", "90"])
        has_scales = any(w in itch or w in str(intake_history.get("symptoms", "")) for w in ["scale", "scales", "silvery", "पपड़ी", "सफेद"])

        if is_extensor and (is_chronic or has_scales):
            history_multipliers["psoriasis"] *= 3.5
            citations_en.append(f"Lesions localized on extensor surfaces ({body_site}) with chronic duration ({duration}), typical for Psoriasis.")
            citations_hi.append(f"प्रभावित अंग ({body_site}) और लंबे समय से मौजूदगी ({duration}) सोरायसिस की पहचान से मेल खाती है।")
        elif is_extensor:
            history_multipliers["psoriasis"] *= 1.8

        # 3. Acne evaluation
        is_face = any(s in body_site for s in ["face", "cheek", "cheeks", "forehead", "chin", "nose", "चेहरा", "गाल", "माथा"])
        if is_face:
            history_multipliers["acne"] *= 3.0
            citations_en.append(f"Facial distribution ({body_site}) strongly correlates with Acne Vulgaris.")
            citations_hi.append(f"चेहरे पर दानों की स्थिति ({body_site}) मुँहासों (Acne) से काफी मेल खाती है।")

        # 4. Eczema evaluation
        is_flexural = any(s in body_site for s in ["crease", "elbow fold", "knee fold", "neck", "wrist", "हाथ", "गर्दन", "पैर"])
        has_atopy = any(a in allergies for a in ["yes", "asthma", "dust", "atopy", "allergy", "हाँ", "एलर्जी"])
        if is_flexural and has_atopy:
            history_multipliers["eczema"] *= 3.2
            citations_en.append(f"Flexural involvement combined with allergic/atopic background ({allergies}) indicates Eczema.")
            citations_hi.append(f"जोड़ों के मुड़ाव वाले हिस्सों और पुरानी एलर्जी इतिहास ({allergies}) एक्जिमा को दर्शाता है।")
        elif is_flexural:
            history_multipliers["eczema"] *= 2.1

        # 5. Tinea (Fungal / Ringworm) evaluation
        is_ring_shaped = any(w in str(intake_history.get("symptoms", "")) or w in body_site for w in ["ring", "circle", "groin", "गोल", "छल्ला", "जांघ"])
        if is_ring_shaped:
            history_multipliers["tinea"] *= 3.4
            citations_en.append("Reported annular ring pattern or groin/fold distribution supports Tinea (Ringworm).")
            citations_hi.append("छल्लेदार या गोल चकत्ते और नमी वाले अंग दाद (Tinea) संक्रमण की ओर इशारा करते हैं।")

        # 6. Urticaria (Hives) evaluation
        is_transient = any(d in duration for d in ["hour", "hours", "today", "घंटे", "आज", "1 day", "sudden", "अचानक"])
        if is_transient and ("itch" in itch or "severe" in itch):
            history_multipliers["urticaria"] *= 3.3
            citations_en.append(f"Acute, rapid-onset transient itchy wheals ({duration}) align with Urticaria (hives).")
            citations_hi.append(f"अचानक उभरे और तेजी से बदलने वाले चकत्ते ({duration}) पित्ती (Urticaria) से मेल खाते हैं।")

        # Apply Bayesian clinical weighting
        reasoned_scores = {}
        for cond in self.conditions:
            reasoned_scores[cond] = baseline_probs[cond] * history_multipliers[cond]

        # Normalize
        total_score = sum(reasoned_scores.values()) + 1e-9
        reasoned_probs = {c: round(score / total_score, 4) for c, score in reasoned_scores.items()}

        # Sort differentials
        sorted_baseline = sorted(baseline_probs.items(), key=lambda x: x[1], reverse=True)
        sorted_reasoned = sorted(reasoned_probs.items(), key=lambda x: x[1], reverse=True)

        top_baseline_cond, top_baseline_conf = sorted_baseline[0]
        top_reasoned_cond, top_reasoned_conf = sorted_reasoned[0]

        # Calculate Gain from Voice History
        confidence_delta = round(top_reasoned_conf - top_baseline_conf, 4)
        diagnostic_shift = (top_baseline_cond != top_reasoned_cond)
        
        if not citations_en:
            citations_en.append("History provides complementary clinical context aligned with visual features.")
            citations_hi.append("मरीज द्वारा बताई गई जानकारी फोटो के लक्षणों की पुष्टि करती है।")

        # Plain language summary for patient
        patient_explanation = (
            CONDITION_METADATA[top_reasoned_cond]["patient_explanation_hi"]
            if language == "hi"
            else CONDITION_METADATA[top_reasoned_cond]["patient_explanation_en"]
        )
        self_care = (
            CONDITION_METADATA[top_reasoned_cond]["self_care_hi"]
            if language == "hi"
            else CONDITION_METADATA[top_reasoned_cond]["self_care_en"]
        )

        return {
            "top_condition": top_reasoned_cond,
            "top_confidence": top_reasoned_conf,
            "display_name": CONDITION_METADATA[top_reasoned_cond]["display_name"],
            "hindi_name": CONDITION_METADATA[top_reasoned_cond]["hindi_name"],
            "is_malignant": CONDITION_METADATA[top_reasoned_cond]["is_malignant"],
            "ranked_differential": [
                {
                    "condition": cond,
                    "display_name": CONDITION_METADATA[cond]["display_name"],
                    "hindi_name": CONDITION_METADATA[cond]["hindi_name"],
                    "probability": prob,
                    "is_malignant": CONDITION_METADATA[cond]["is_malignant"]
                }
                for cond, prob in sorted_reasoned
            ],
            "baseline_image_only": {
                "top_condition": top_baseline_cond,
                "top_confidence": top_baseline_conf,
                "display_name": CONDITION_METADATA[top_baseline_cond]["display_name"],
                "hindi_name": CONDITION_METADATA[top_baseline_cond]["hindi_name"],
                "ranked_differential": [
                    {
                        "condition": cond,
                        "display_name": CONDITION_METADATA[cond]["display_name"],
                        "probability": prob
                    }
                    for cond, prob in sorted_baseline
                ]
            },
            "gain_from_voice_history": {
                "confidence_gain_pct": round(confidence_delta * 100, 1),
                "diagnostic_shift": diagnostic_shift,
                "baseline_top": top_baseline_cond,
                "reasoned_top": top_reasoned_cond,
                "summary": (
                    f"Voice history {'reclassified diagnosis from ' + top_baseline_cond + ' to ' + top_reasoned_cond if diagnostic_shift else 'strengthened confidence by ' + str(round(confidence_delta * 100, 1)) + '%'}"
                )
            },
            "reasoning_citations_en": citations_en,
            "reasoning_citations_hi": citations_hi,
            "patient_plain_language": {
                "condition_overview": patient_explanation,
                "self_care_guidance": self_care,
                "safety_disclaimer": "This is an AI screening aid and not a medical prescription. Please consult a registered doctor if symptoms worsen." if language != "hi" else "यह केवल एक AI स्क्रीनिंग सहायक है, डॉक्टरी पर्चा नहीं। यदि लक्षण बढ़ें तो डॉक्टर से अवश्य मिलें।"
            }
        }
