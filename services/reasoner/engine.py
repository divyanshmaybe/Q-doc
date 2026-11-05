"""
Clinical Diagnosis Reasoner Engine for Q-Doc MVP.
Combines ClinicalIntakeSlots and ImagePrediction into a constrained
multimodal clinical differential, citing inputs, enforcing closed taxonomy,
and proving Gain from Voice History.
"""

import json
from typing import Dict, Any, List, Optional
from services.dialogue.schemas import (
    SkinCondition,
    ClinicalIntakeSlots,
    ImagePrediction,
    DifferentialDiagnosisItem,
    ClinicalReasonerOutput
)
from services.policy.rules import sanitize_safety_constraints
from services.clinical_knowledge.treatment_protocols import get_treatment_guidance

# Plain language explanations in Hindi and English (Free of drug dosages & prescriptions!)
CONDITION_EXPLANATIONS = {
    SkinCondition.ACNE: {
        "hi": "यह स्थिति मुँहासे (Acne) से काफी मेल खाती है, जो त्वचा के रोमछिद्रों में तेल जमा होने से होती है। चेहरे को दिन में दो बार सौम्य क्लीन्ज़र से धोएं।",
        "en": "The symptoms align with Acne Vulgaris, where oil and dead skin cells block pores. Wash face twice daily with a mild cleanser."
    },
    SkinCondition.ECZEMA: {
        "hi": "यह एक्जिमा (Eczema / त्वचा की सूजन) के लक्षण हैं। नियमित रूप से सौम्य मॉइस्चराइज़र लगाएं और तेज साबुन के प्रयोग से बचें।",
        "en": "The findings are consistent with Eczema (Atopic Dermatitis). Apply gentle moisturizers regularly and avoid harsh scented soaps."
    },
    SkinCondition.PSORIASIS: {
        "hi": "यह लक्षण सोरायसिस (Psoriasis) से मेल खाते हैं। त्वचा को पर्याप्त नम रखें और खरोंचने से बचें।",
        "en": "The presentation is consistent with Psoriasis Vulgaris. Keep the affected skin hydrated and avoid skin trauma."
    },
    SkinCondition.TINEA: {
        "hi": "यह दाद (Tinea / फंगल इन्फेक्शन) की संभावना दर्शाता है। प्रभावित हिस्से को हमेशा सूखा व साफ रखें और निजी कपड़े साझा न करें।",
        "en": "These ring-like patches suggest Tinea (Fungal Ringworm). Keep the area clean and completely dry."
    },
    SkinCondition.URTICARIA: {
        "hi": "यह अचानक उभरने वाली पित्ती (Urticaria / Hives) का संकेत है। खुजली शांत करने के लिए ठंडी सिकाई करें और तेज गर्मी से बचें।",
        "en": "These transient wheals indicate Urticaria (Hives). Apply cool compresses to soothe the skin."
    },
    SkinCondition.SCABIES: {
        "hi": "रात में तेज खुजली और परिवार के सदस्यों में समान लक्षण स्केबीज (Scabies) संक्रमण का संकेत देते हैं। बिस्तर के कपड़े गर्म पानी में धोएं और परिवार सहित डॉक्टर से मिलें।",
        "en": "Severe nocturnal itching with household members affected strongly indicates Scabies infestation. Wash bed linens in hot water and consult a physician together."
    },
    SkinCondition.POSSIBLE_MALIGNANCY: {
        "hi": "त्वचा पर दिख रहे इस असामान्य निशान की त्वचा रोग विशेषज्ञ (Dermatologist) द्वारा प्रत्यक्ष जांच आवश्यक है।",
        "en": "This atypical lesion requires direct professional examination by a dermatologist. Please arrange a clinical visit."
    },
    SkinCondition.OTHER_UNCLEAR: {
        "hi": "लक्षण स्पष्ट श्रेणी में नहीं आते हैं। सटीक पहचान के लिए डॉक्टर से प्रत्यक्ष जांच करवाएं।",
        "en": "The presentation does not cleanly fit standard patterns. A doctor's evaluation is recommended."
    }
}

class ClinicalReasonerEngine:
    def __init__(self):
        self.allowed_conditions = list(SkinCondition)

    def reason(
        self,
        intake: ClinicalIntakeSlots,
        img_pred: ImagePrediction
    ) -> ClinicalReasonerOutput:
        """
        Multimodal clinical Bayesian reasoning combining patient intake with image probabilities.
        Enforces closed taxonomy, hard red flags, negative guardrails, and history citations.
        """
        is_hi = "hi" in (intake.primary_language or "").lower()
        red_flags: List[str] = []
        justifications: Dict[SkinCondition, List[str]] = {c: [] for c in self.allowed_conditions}

        # Baseline Image prediction
        baseline_top = img_pred.top_condition
        baseline_conf = img_pred.confidence

        # Clinical multipliers initialized to baseline
        multipliers = {c: 1.0 for c in self.allowed_conditions}

        # 1. Scabies Clinical Triad: nocturnal itch, web-spaces/wrist, household contacts affected (Test Case 1)
        is_scabies_site = intake.body_site in ["hands", "wrists", "web", "fingers"]
        has_household = bool(intake.household_contacts_affected)
        has_itch = bool(intake.has_itching)

        if has_itch and has_household:
            # Huge clinical boost for Scabies transmission triad
            multipliers[SkinCondition.SCABIES] *= 6.0
            # Eczema rarely clusters acutely in household contacts
            multipliers[SkinCondition.ECZEMA] *= 0.35
            justifications[SkinCondition.SCABIES].append(
                "Patient reported itching with household contacts affected (classic transmission triad of Scabies)." if not is_hi else
                "मरीज ने खुजली और परिवार में समान लक्षण बताए (स्केबीज का प्रमुख लक्षण)।"
            )
        elif is_scabies_site and has_itch:
            multipliers[SkinCondition.SCABIES] *= 2.5
            justifications[SkinCondition.SCABIES].append(
                "Lesion localized on hand/wrist web spaces with pruritus." if not is_hi else
                "हाथ व कलाई की उंगलियों के बीच खुजलीदार दाने।"
            )

        # 2. Fever with rash Red Flag (Test Case 3)
        if intake.has_fever:
            red_flags.append("fever_with_rash")
            # Systemic rash or urticaria / viral exanthem
            multipliers[SkinCondition.OTHER_UNCLEAR] *= 1.8

        # 3. Possible Malignancy Red Flag (Test Case 2)
        if (
            baseline_top == SkinCondition.POSSIBLE_MALIGNANCY or
            img_pred.probabilities.get(SkinCondition.POSSIBLE_MALIGNANCY, 0.0) >= 0.35
        ):
            red_flags.append("possible_malignancy")
            multipliers[SkinCondition.POSSIBLE_MALIGNANCY] *= 3.0
            justifications[SkinCondition.POSSIBLE_MALIGNANCY].append(
                "Visual analysis indicates atypical asymmetry and irregular pigmentation requiring dermatologist referral." if not is_hi else
                "फोटो में असामान्य निशान और असमान रंगत डॉक्टर से प्रत्यक्ष जांच की मांग करते हैं।"
            )

        # 4. Acne distribution
        if intake.body_site == "face":
            multipliers[SkinCondition.ACNE] *= 3.2
            justifications[SkinCondition.ACNE].append("Facial distribution supports Acne Vulgaris.")

        # 5. Psoriasis extensor surfaces & chronic duration
        if intake.body_site in ["arms", "legs", "elbows", "knees"] and (intake.duration_days or 0) >= 30:
            multipliers[SkinCondition.PSORIASIS] *= 3.5
            justifications[SkinCondition.PSORIASIS].append("Chronic plaque duration on extensor joints typical of Psoriasis.")

        # 6. Tinea groin / annular
        if intake.body_site in ["groin", "torso"]:
            multipliers[SkinCondition.TINEA] *= 2.4
            justifications[SkinCondition.TINEA].append("Intertriginous/body distribution characteristic of Tinea.")

        # 7. Urticaria acute transient duration
        if (intake.duration_days or 0) <= 2 and has_itch:
            multipliers[SkinCondition.URTICARIA] *= 2.8
            justifications[SkinCondition.URTICARIA].append("Acute rapid-onset pruritic wheals typical of Urticaria.")

        # 8. Seborrheic Dermatitis / Facial Flaking (maps to Eczema/Dermatitis spectrum)
        if intake.body_site in ["face", "scalp"] and (intake.duration_days or 0) >= 7:
            lesion_desc = getattr(intake, "lesion_type", "") or ""
            if any(w in lesion_desc.lower() for w in ["flaky", "flaking", "dandruff", "scaly", "rough and flaky", "रूसी", "पपड़ी"]):
                multipliers[SkinCondition.ECZEMA] *= 2.0
                justifications[SkinCondition.ECZEMA].append(
                    "Flaking/scaling on face or scalp consistent with seborrheic / eczematous dermatitis." if not is_hi else
                    "चेहरे या सिर पर पपड़ीदार त्वचा एक्जिमा/डर्मेटाइटिस से मेल खाती है।"
                )

        # 9. Tinea Cruris (Groin / Fungal) — extremely common in Indian tropical climate
        if intake.body_site == "groin" and has_itch:
            multipliers[SkinCondition.TINEA] *= 3.5
            justifications[SkinCondition.TINEA].append(
                "Pruritic groin rash characteristic of Tinea Cruris (fungal jock itch)." if not is_hi else
                "जांघों के बीच खुजलीदार दाने टिनिया क्रूरिस (फंगल संक्रमण) का प्रमुख संकेत हैं।"
            )

        # 10. Contact Dermatitis (Hands / localized, non-contagious)
        if intake.body_site in ["hands", "wrists"] and has_itch and not has_household and (intake.duration_days or 0) <= 14:
            multipliers[SkinCondition.ECZEMA] *= 1.8
            justifications[SkinCondition.ECZEMA].append(
                "Localized hand itching without household clustering suggests contact dermatitis / hand eczema." if not is_hi else
                "हाथों पर बिना पारिवारिक प्रसार की खुजली कॉन्टैक्ट डर्मेटाइटिस की संभावना दर्शाती है।"
            )

        # 11. Pityriasis Versicolor / Trunk Hypopigmentation (common superficial mycosis in India)
        if intake.body_site in ["torso", "chest", "back"] and (intake.duration_days or 0) >= 14:
            lesion_desc = getattr(intake, "lesion_type", "") or ""
            if any(w in lesion_desc.lower() for w in ["discoloration", "white", "patch", "pigment", "धब्बा", "सफ़ेद"]):
                multipliers[SkinCondition.TINEA] *= 2.2
                justifications[SkinCondition.TINEA].append(
                    "Chronic discolored patches on torso characteristic of superficial fungal pityriasis." if not is_hi else
                    "धड़ पर पुराने सफ़ेद/हल्के धब्बे फंगल पिटिरियासिस का संकेत हैं।"
                )

        # 12. Scabies nocturnal pruritus enhancement
        if has_itch:
            lesion_desc = getattr(intake, "lesion_type", "") or ""
            if any(w in lesion_desc.lower() for w in ["night", "nocturnal", "raat", "रात"]):
                multipliers[SkinCondition.SCABIES] *= 2.2
                justifications[SkinCondition.SCABIES].append(
                    "Nocturnal itch exacerbation strongly supports Sarcoptes scabiei infestation." if not is_hi else
                    "रात में तेज खुजली स्केबीज का विशिष्ट लक्षण है।"
                )

        # 13. ABCDE Melanoma Detection from morphology & qualifiers
        lesion_desc = getattr(intake, "lesion_type", "") or ""
        combined_text = f"{lesion_desc}".lower()
        melanoma_keywords = ["asymmetric", "irregular border", "uneven", "multiple colors", "changing color", "dark spot/mole"]
        if any(kw in combined_text for kw in ["dark spot/mole", "काला तिल/धब्बा"]) and getattr(intake, 'is_spreading', False):
            red_flags.append("possible_malignancy")
            multipliers[SkinCondition.POSSIBLE_MALIGNANCY] *= 4.0
            justifications[SkinCondition.POSSIBLE_MALIGNANCY].append(
                "Changing or spreading pigmented lesion meets ABCDE criteria for urgent dermatologist biopsy referral." if not is_hi else
                "फैलता हुआ काला तिल/दाग मेलेनोमा के खतरे के अंतर्गत तत्काल डॉक्टर की जांच मांगता है।"
            )

        # 14. Rapid spread red flag
        if getattr(intake, 'is_spreading', False) and (intake.duration_days or 0) <= 3:
            red_flags.append("rapid_spread")
            multipliers[SkinCondition.OTHER_UNCLEAR] *= 1.8
            justifications[SkinCondition.OTHER_UNCLEAR].append(
                "Rapidly expanding acute rash flagged for urgent clinical review." if not is_hi else
                "तेज़ी से फैलता तीव्र चकत्ता तत्काल क्लिनिकल समीक्षा की मांग करता है।"
            )

        # 15. Infant under 1 year red flag
        if intake.age is not None and intake.age < 1:
            red_flags.append("infant_under_1_year")

        # Compute posterior scores
        final_scores: Dict[SkinCondition, float] = {}
        for cond in self.allowed_conditions:
            img_p = float(img_pred.probabilities.get(cond, 0.05))
            final_scores[cond] = img_p * multipliers[cond]

        # Normalize
        total_score = sum(final_scores.values()) + 1e-9
        calibrated_probs = {c: round(score / total_score, 4) for c, score in final_scores.items()}

        # Build differential items
        sorted_probs = sorted(calibrated_probs.items(), key=lambda x: x[1], reverse=True)
        differential: List[DifferentialDiagnosisItem] = []

        for cond, prob in sorted_probs:
            just_list = justifications.get(cond, [])
            if not just_list:
                just_text = f"Visual classifier probability ({prob:.1%}) with complementary intake concordance."
            else:
                just_text = " ".join(just_list)
            differential.append(DifferentialDiagnosisItem(
                condition=cond,
                probability=prob,
                clinical_justification=just_text
            ))

        top_diagnosis = sorted_probs[0][0]
        final_confidence = sorted_probs[0][1]

        # Gain from Voice History calculation
        shifted = (top_diagnosis != baseline_top)
        conf_delta = round(final_confidence - baseline_conf, 3)
        if shifted:
            gain_summary = f"Voice history reclassified diagnosis from {baseline_top.value} to {top_diagnosis.value} (+{round(conf_delta*100, 1)}% confidence lift)"
        else:
            gain_summary = f"Voice history strengthened {top_diagnosis.value} confidence by {round(conf_delta*100, 1)}%"

        # Empathetic, simple plain-language explanation without medical jargon
        explanation_dict = CONDITION_EXPLANATIONS.get(top_diagnosis, CONDITION_EXPLANATIONS[SkinCondition.OTHER_UNCLEAR])
        explanation = explanation_dict["hi"] if is_hi else explanation_dict["en"]

        # Append actionable evidence-based treatment and self-care guidance for common benign conditions
        if top_diagnosis != SkinCondition.POSSIBLE_MALIGNANCY and "possible_malignancy" not in red_flags:
            treatment_advice = get_treatment_guidance(top_diagnosis, lang="hi" if is_hi else "en")
            explanation = f"{explanation} {treatment_advice}"

        # CRITICAL NEGATIVE GUARDRAIL (Test Case 5): Enforce zero drug dosages or prescriptions
        sanitized_explanation = sanitize_safety_constraints(explanation)

        return ClinicalReasonerOutput(
            differential=differential,
            top_diagnosis=top_diagnosis,
            final_confidence=final_confidence,
            identified_red_flags=sorted(list(set(red_flags))),
            synthesized_explanation=sanitized_explanation,
            baseline_image_top=baseline_top,
            baseline_image_confidence=baseline_conf,
            gain_from_voice_history=gain_summary
        )

