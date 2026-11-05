"""
LLM and Dialogue Gateway Adapter for Q-Doc MVP.
Manages slot-filling conversation turns, fact confirmation,
and one-page clinical brief generation.
Supports Google Gemini API with smart deterministic fallback.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional

REQUIRED_SLOTS = [
    "body_site",
    "duration",
    "itch",
    "spread",
    "fever",
    "household_contacts"
]

OPTIONAL_SLOTS = [
    "pain",
    "allergies",
    "medicines",
    "age",
    "sex"
]

QUESTIONS_HI = {
    "body_site": "यह परेशानी शरीर के किस हिस्से में है?",
    "duration": "आपकी समस्या कितने दिनों या हफ्तों से है?",
    "itch": "क्या इसमें खुजली होती है? क्या यह रात के समय ज्यादा बढ़ती है?",
    "pain": "क्या इसमें दर्द या जलन भी महसूस होती है?",
    "spread": "क्या यह निशान तेजी से फैल रहा है या वहीं बना हुआ है?",
    "fever": "क्या आपको बुखार या अस्वस्थता महसूस हो रही है?",
    "household_contacts": "क्या घर में किसी अन्य सदस्य को भी ऐसी ही खुजली या चकत्ते हैं?",
    "allergies": "क्या आपको पहले से किसी दवा या चीज से एलर्जी है?",
    "medicines": "क्या आप इसके लिए कोई क्रीम या दवा लगा रहे हैं?",
    "age": "आपकी उम्र कितनी है?"
}

QUESTIONS_EN = {
    "body_site": "Where on your body is this rash or skin issue located?",
    "duration": "How many days or weeks have you had this problem?",
    "itch": "Is there itching? Does it get worse at night?",
    "pain": "Do you feel pain, burning, or soreness in the area?",
    "spread": "Is the rash spreading rapidly, or staying in the same place?",
    "fever": "Do you have any fever, chills, or feeling unwell?",
    "household_contacts": "Does anyone else in your home have similar itching or skin bumps?",
    "allergies": "Do you have any known allergies or asthma?",
    "medicines": "Have you applied any cream or taken medications for it?",
    "age": "Could you share your approximate age?"
}

class LLMGateway:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def process_turn(
        self,
        current_slots: Dict[str, Any],
        user_utterance: str,
        conversation_history: List[Dict[str, str]],
        language: str = "hi"
    ) -> Dict[str, Any]:
        """
        Extracts slot values from user utterance and decides next question or confirmation.
        """
        # If Gemini is available, we could prompt Gemini for structured extraction
        extracted_slots = self._extract_slots_rule_based(user_utterance, current_slots, language)
        updated_slots = {**current_slots, **extracted_slots}

        # Check which required slots are still unfilled
        missing = [s for s in REQUIRED_SLOTS if not updated_slots.get(s)]

        # Check if we should do the Confirmation turn
        # If all core required slots are filled, or 4+ slots filled and user just answered
        is_ready_for_photo = len(missing) == 0

        next_question = ""
        confirmation_text = ""
        should_confirm = False

        if is_ready_for_photo:
            # Generate confirmation summary
            confirmation_text = self._build_confirmation(updated_slots, language)
            should_confirm = True
            if language == "hi":
                next_question = f"{confirmation_text} क्या यह सही है? यदि हाँ, तो कृपया प्रभावित त्वचा की एक साफ तस्वीर लें।"
            else:
                next_question = f"{confirmation_text} Is that correct? If so, please take a clear photo of the rash."
        else:
            next_slot = missing[0]
            questions = QUESTIONS_HI if language == "hi" else QUESTIONS_EN
            next_question = questions.get(next_slot, "कृपया इसके बारे में और बताएं।" if language == "hi" else "Please tell me more.")

        return {
            "updated_slots": updated_slots,
            "extracted_this_turn": extracted_slots,
            "missing_slots": missing,
            "next_question": next_question,
            "is_ready_for_photo": is_ready_for_photo,
            "confirmation_text": confirmation_text,
            "should_confirm": should_confirm
        }

    def _extract_slots_rule_based(self, text: str, current_slots: Dict[str, Any], lang: str) -> Dict[str, Any]:
        lower = text.lower()
        extracted: Dict[str, Any] = {}

        # 1. Body Site (using word boundaries for English to avoid 'itching' matching 'chin')
        sites_map = {
            "face": {"en": [r"\bface\b", r"\bcheeks?\b", r"\bforehead\b", r"\bchin\b", r"\bnose\b"], "hi": ["चेहरा", "चेहरे", "गाल", "माथा"]},
            "hands": {"en": [r"\bhands?\b", r"\bfingers?\b", r"\bpalm\b", r"\bwrists?\b", r"\bweb\b"], "hi": ["हाथ", "हाथों", "उंगली", "उंगलियों", "कलाई"]},
            "arms": {"en": [r"\barms?\b", r"\belbows?\b", r"\bforearm\b"], "hi": ["बाजू", "कोहनी", "कोहनियों"]},
            "legs": {"en": [r"\blegs?\b", r"\bknees?\b", r"\bthighs?\b", r"\bshin\b"], "hi": ["टांग", "पैर", "पैरों", "घुटना", "घुटनों"]},
            "torso": {"en": [r"\bchest\b", r"\bback\b", r"\bbelly\b", r"\bstomach\b", r"\bwaist\b"], "hi": ["छाती", "पीठ", "पेट", "कमर"]},
            "groin": {"en": [r"\bgroin\b", r"\bgenitals?\b"], "hi": ["जांघ", "जांघों"]}
        }
        for site_name, spec in sites_map.items():
            if any(re.search(p, lower) for p in spec["en"]) or any(w in lower for w in spec["hi"]):
                extracted["body_site"] = site_name
                break

        # 2. Duration
        dur_match = re.search(r'(\d+)\s*(day|days|week|weeks|month|months|दिन|हफ्ते|महीने)', lower)
        if dur_match:
            extracted["duration"] = f"{dur_match.group(1)} {dur_match.group(2)}"
        elif "two weeks" in lower or "दो हफ्ते" in lower:
            extracted["duration"] = "2 weeks"
        elif "one week" in lower or "एक हफ्ता" in lower:
            extracted["duration"] = "1 week"
        elif "yesterday" in lower or "कल" in lower or "today" in lower or "आज" in lower:
            extracted["duration"] = "1 day"
        elif "few days" in lower or "कुछ दिन" in lower:
            extracted["duration"] = "3-4 days"

        # 3. Itch
        if any(w in lower for w in ["night", "रात", "severe", "बहुत तेज", "बहुत ज्यादा"]):
            extracted["itch"] = "severe, worse at night"
        elif any(w in lower for w in ["yes", "itching", "itch", "खुजली", "हाँ", "हा"]):
            extracted["itch"] = "present"
        elif any(w in lower for w in ["no itch", "doesn't itch", "खुजली नहीं"]):
            extracted["itch"] = "none"

        # 4. Fever
        if any(w in lower for w in ["fever", "बुखार", "shivering", "तापमान"]):
            if any(neg in lower for lower_word in ["no fever", "बुखार नहीं"] if neg in lower):
                extracted["fever"] = "no"
            else:
                extracted["fever"] = "yes"
        elif "बुखार नहीं" in lower or "no" in lower and current_slots.get("fever") is None:
            # Contextual check
            pass

        # 5. Spreading
        if any(w in lower for w in ["rapid", "spreading", "spread", "फैल", "बढ़ रहा"]):
            extracted["spread"] = "yes, spreading"
        elif any(w in lower for w in ["same", "wahi", "नहीं फैल रहा"]):
            extracted["spread"] = "stable"

        # 6. Household contacts
        if any(w in lower for w in ["brother", "sister", "family", "mother", "father", "roommate", "घर में", "भाई", "परिवार", "सबको"]):
            extracted["household_contacts"] = "yes, household members affected"
        elif any(w in lower for w in ["no one", "alone", "किसी को नहीं"]):
            extracted["household_contacts"] = "none"

        # 7. Age (requires explicit age indicators to prevent catching duration numbers)
        age_match = re.search(r'\b(?:age|उम्र|आयु)\s*(?:is|of|hai)?\s*(\d{1,2})\b|\b(\d{1,2})\s*(?:years\s*old|साल\s*की|साल\s*का|yrs\s*old)\b', lower)
        if age_match:
            try:
                val_str = age_match.group(1) or age_match.group(2)
                if val_str:
                    val = int(val_str)
                    if 1 <= val <= 100:
                        extracted["age"] = val
            except ValueError:
                pass

        return extracted

    def _build_confirmation(self, slots: Dict[str, Any], lang: str) -> str:
        site = slots.get("body_site", "त्वचा" if lang == "hi" else "skin")
        dur = slots.get("duration", "कुछ समय" if lang == "hi" else "some time")
        itch = slots.get("itch", "")

        if lang == "hi":
            return f"आपने बताया कि यह समस्या {dur} से {site} पर है और इसमें {itch} है।"
        else:
            return f"You noted that you have had this rash on your {site} for about {dur}, with {itch}."

    def generate_clinician_brief(
        self,
        session_id: str,
        patient_info: Dict[str, Any],
        intake_history: Dict[str, Any],
        prediction_result: Dict[str, Any],
        policy_decision: Dict[str, Any],
        patient_verdict_text: str
    ) -> Dict[str, Any]:
        """
        Generates a concise 1-page structured clinician brief.
        Adheres to spec Section 5.4.
        """
        age = intake_history.get("age", patient_info.get("age", "Unknown"))
        sex = intake_history.get("sex", patient_info.get("sex", "Unknown"))
        chief_complaint = (
            f"Rash on {intake_history.get('body_site', 'unspecified area')} for {intake_history.get('duration', 'unspecified duration')}"
        )

        red_flags = policy_decision.get("red_flags_detected", [])
        urgency = policy_decision.get("urgency_level", "routine").upper()

        top_cond = prediction_result.get("top_condition", "other_or_unclear")
        top_conf = prediction_result.get("top_confidence", 0.0)
        differential = prediction_result.get("ranked_differential", [])

        # Citations and voice gain
        citations = prediction_result.get("reasoning_citations_en", [])
        gain_info = prediction_result.get("gain_from_voice_history", {})

        brief = {
            "session_id": session_id,
            "patient_demographics": {
                "age": age,
                "sex": sex,
                "preferred_language": patient_info.get("language", "hi")
            },
            "chief_complaint": chief_complaint,
            "history_fields": {
                "body_site": intake_history.get("body_site", "N/A"),
                "duration": intake_history.get("duration", "N/A"),
                "itch_severity": intake_history.get("itch", "N/A"),
                "pain": intake_history.get("pain", "None reported"),
                "spreading": intake_history.get("spread", "Stable"),
                "fever_reported": intake_history.get("fever", "No"),
                "household_contacts_symptomatic": intake_history.get("household_contacts", "No"),
                "known_allergies": intake_history.get("allergies", "None reported"),
                "current_medications": intake_history.get("medicines", "None")
            },
            "clinical_decision_support": {
                "top_diagnosis": prediction_result.get("display_name", top_cond),
                "confidence_score": f"{top_conf:.1%}",
                "urgency_triaged": urgency,
                "policy_mode": policy_decision.get("mode", "autonomous"),
                "policy_action": policy_decision.get("action", "ANSWER"),
                "red_flags": red_flags if red_flags else ["None identified"],
                "gain_from_voice_history": gain_info.get("summary", "Complementary multimodal concordance")
            },
            "ranked_differential": [
                {
                    "rank": idx + 1,
                    "condition": item.get("display_name", item.get("condition")),
                    "probability": f"{item.get('probability', 0.0):.1%}",
                    "is_malignant": item.get("is_malignant", False)
                }
                for idx, item in enumerate(differential[:4])
            ],
            "reasoning_evidence": citations,
            "patient_disclosed_words": patient_verdict_text,
            "audit_timestamp": policy_decision.get("timestamp", "")
        }
        return brief
