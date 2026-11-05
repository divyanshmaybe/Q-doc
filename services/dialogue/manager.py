"""
Dialogue Manager for Q-Doc MVP.
Slot-filling state machine & conversational turn controller with persistent back memory.
Continuously gathers required biomarkers across turns, acknowledges what has been
obtained so far, dynamically inquires about missing details, limits turns to 6,
and issues the confirmation turn for lesion photo triage.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .schemas import ClinicalIntakeSlots
from services.policy.rules import sanitize_safety_constraints
from services.gateway.llm import LLMAdapter
from .clinical_agent import UtteranceNormalizer, HeadDermatologistAgent

REQUIRED_SLOTS = [
    "body_site",
    "duration_days",
    "has_itching",
    "has_fever",
    "household_contacts_affected"
]

QUESTIONS_HI = {
    "body_site": "यह परेशानी शरीर के किस हिस्से में है (जैसे हाथ, चेहरा, पैर)?",
    "duration_days": "आपकी यह समस्या कितने दिनों या हफ्तों से है?",
    "has_itching": "क्या इसमें खुजली होती है? क्या यह रात के समय ज्यादा बढ़ती है?",
    "has_fever": "क्या आपको बुखार या अस्वस्थता महसूस हो रही है?",
    "household_contacts_affected": "क्या घर में किसी अन्य सदस्य को भी ऐसी ही खुजली या चकत्ते हैं?"
}

QUESTIONS_EN = {
    "body_site": "Where on your body is this rash located (e.g. hands, face, legs)?",
    "duration_days": "How many days or weeks have you had this skin issue?",
    "has_itching": "Is there itching? Does it get worse at night?",
    "has_fever": "Do you have any fever or chills?",
    "household_contacts_affected": "Does anyone else in your home have similar itching or skin bumps?"
}

class DialogueManager:
    def __init__(self, max_turns: Optional[int] = None, llm_adapter: Optional[LLMAdapter] = None):
        self.max_turns = max_turns
        self.llm_adapter = llm_adapter or LLMAdapter()
        self.normalizer = UtteranceNormalizer(self.llm_adapter)
        self.head_agent = HeadDermatologistAgent(self.llm_adapter, max_turns=max_turns)

    def compute_missing_slots(self, slots: ClinicalIntakeSlots) -> List[str]:
        missing = []
        if not slots.body_site:
            missing.append("body_site")
        if slots.duration_days is None:
            missing.append("duration_days")
        if slots.has_itching is None:
            missing.append("has_itching")
        if slots.has_fever is None:
            missing.append("has_fever")
        if slots.household_contacts_affected is None:
            missing.append("household_contacts_affected")
        return missing

    def prioritize_missing_slots(self, slots: ClinicalIntakeSlots, missing: List[str]) -> List[str]:
        """
        Prioritizes remaining missing slots based on clinical urgency and what's in memory:
        1. If acute symptoms or high itch are reported, prioritize red-flag fever check.
        2. If hands/wrists/web-spaces are affected, prioritize contagion (contacts).
        3. If body site is not yet known, collect body site first.
        4. Otherwise follow standard clinical history hierarchy.
        """
        if not missing:
            return []

        # If body site is still unknown, prioritize establishing location
        if "body_site" in missing:
            order = ["body_site"] + [s for s in missing if s != "body_site"]
            return order

        def score_slot(slot: str) -> int:
            if slot == "has_fever":
                if slots.duration_days is not None and slots.duration_days <= 3:
                    return 100
                return 40
            if slot == "household_contacts_affected":
                if slots.body_site in ["hands", "wrists"] and slots.has_itching:
                    return 90
                return 30
            if slot == "duration_days":
                return 60
            if slot == "has_itching":
                return 50
            return 10

        return sorted(missing, key=score_slot, reverse=True)

    def process_turn(
        self,
        current_slots: ClinicalIntakeSlots,
        user_utterance: str,
        last_question_slot: Optional[str] = None
    ) -> Tuple[ClinicalIntakeSlots, str, bool, Optional[str]]:
        """
        Two-Tier Processing:
        Tier 1: UtteranceNormalizer fixes speech errors and extracts clinical intent.
        Tier 2: HeadDermatologistAgent updates memory, consults knowledge base, and
                generates the next clinically reasoned inquiry or confirmation turn.
        """
        lang = "hi" if "hi" in current_slots.primary_language.lower() else "en"

        # Tier 1: Clean & resolve user intent
        norm_res = self.normalizer.normalize(
            raw_transcript=user_utterance,
            last_agent_question=last_question_slot,
            language=lang
        )

        # Fallback slot extraction to guarantee robust memory capture
        self._extract_slots(user_utterance, current_slots, lang, last_question_slot)

        # Tier 2: Head Dermatologist Agent step
        slots, agent_msg, is_ready, confirm_prompt = self.head_agent.step(
            slots=current_slots,
            normalized_intent=norm_res,
            turn_history=[],
            lang=lang
        )

        # Compute remaining missing slots for UI state synchronization
        if is_ready:
            slots.missing_required_slots = []
        else:
            missing = self.compute_missing_slots(slots)
            prioritized_missing = self.prioritize_missing_slots(slots, missing)
            slots.missing_required_slots = prioritized_missing
        slots.is_complete = is_ready

        return slots, agent_msg, is_ready, confirm_prompt

    def _generate_adaptive_question(
        self,
        prioritized_missing: List[str],
        slots: ClinicalIntakeSlots,
        user_utterance: str,
        lang: str
    ) -> str:
        """
        Formulates the next question by:
        1. Actively acknowledging the clinical details obtained till now in back memory,
           referencing the user's specific symptom morphology (e.g. rough/flaky skin,
           pimples, dark spot, etc.) rather than generic 'rash'.
        2. Naturally inquiring about what still needs to be known.
        3. Enforcing strict safety guardrails.
        """
        problem_en = getattr(slots, "lesion_type", None) or "skin condition"
        problem_hi = getattr(slots, "lesion_type", None) or "त्वचा की समस्या"

        # --- Part 1: Acknowledge what has been obtained so far ---
        ack = ""
        if lang == "hi":
            site_names_hi = {
                "legs": "पैरों", "hands": "हाथों", "arms": "हाथ/बाजू",
                "face": "चेहरे", "torso": "छाती/पीठ", "groin": "जांघों/कमर", "whole_body": "शरीर"
            }
            site_hi = site_names_hi.get(slots.body_site or "", slots.body_site or "त्वचा")
            if slots.body_site:
                if slots.has_itching is True and slots.duration_days:
                    d_str = f"{slots.duration_days // 7} हफ्ते" if slots.duration_days >= 7 and slots.duration_days % 7 == 0 else f"{slots.duration_days} दिन"
                    ack = f"मैंने आपके {site_hi} पर {d_str} से खुजली वाली {problem_hi} को नोट कर लिया है।"
                elif slots.duration_days:
                    d_str = f"{slots.duration_days // 7} हफ्ते" if slots.duration_days >= 7 and slots.duration_days % 7 == 0 else f"{slots.duration_days} दिन"
                    ack = f"मैंने आपके {site_hi} पर लगभग {d_str} से {problem_hi} को नोट कर लिया है।"
                elif slots.has_itching is True:
                    ack = f"मैंने आपके {site_hi} पर खुजली वाली {problem_hi} को नोट कर लिया है।"
                else:
                    ack = f"मैंने आपके {site_hi} पर {problem_hi} को नोट कर लिया है।"
        else:
            if slots.body_site:
                itch_desc = "with itching " if slots.has_itching is True else ""
                if slots.duration_days:
                    d_str = f"{slots.duration_days // 7} week(s)" if slots.duration_days >= 7 and slots.duration_days % 7 == 0 else f"{slots.duration_days} days"
                    ack = f"I've noted the {problem_en} on your {slots.body_site} {itch_desc}for {d_str}."
                elif slots.has_itching is True:
                    ack = f"Got it, {problem_en} on your {slots.body_site} with itching."
                else:
                    ack = f"I've noted the {problem_en} on your {slots.body_site}."

        # --- Part 2: Formulate inquiry for what still needs to be known ---
        ask = ""
        if lang == "hi":
            if "body_site" in prioritized_missing:
                ask = "यह परेशानी आपके शरीर के किस हिस्से में है (जैसे चेहरा, हाथ, पैर, या पीठ)?"
            elif "duration_days" in prioritized_missing and "has_itching" in prioritized_missing:
                ask = "यह समस्या लगभग कितने दिनों या हफ्तों से है, और क्या इसमें खुजली होती है?"
            elif "duration_days" in prioritized_missing:
                ask = "यह समस्या कितने दिनों या हफ्तों से बनी हुई है?"
            elif "has_itching" in prioritized_missing:
                ask = "क्या इसमें खुजली होती है, विशेष रूप से शाम या रात के समय?"
            elif "has_fever" in prioritized_missing and "household_contacts_affected" in prioritized_missing:
                ask = "क्या आपको कोई बुखार या ठंड लगना महसूस हुआ है, और क्या घर में किसी अन्य सदस्य को भी ऐसी समस्या है?"
            elif "has_fever" in prioritized_missing:
                ask = "क्या आपको इसके साथ कोई बुखार, ठंड या कंपकंपी महसूस हुई है?"
            elif "household_contacts_affected" in prioritized_missing:
                ask = "क्या आपके घर या परिवार में किसी अन्य सदस्य को भी ऐसी ही समस्या है?"
            else:
                next_slot = prioritized_missing[0]
                ask = QUESTIONS_HI.get(next_slot, "कृपया इसके बारे में और बताएं।")
        else:
            if "body_site" in prioritized_missing:
                ask = "Which part of your body is most affected (e.g. face, arms, legs, torso)?"
            elif "duration_days" in prioritized_missing and "has_itching" in prioritized_missing:
                ask = "How long has it been there, and does it feel itchy?"
            elif "duration_days" in prioritized_missing:
                ask = "Approximately how many days or weeks have you had this skin issue?"
            elif "has_itching" in prioritized_missing:
                ask = "Does the affected area itch, and does it get worse at night?"
            elif "has_fever" in prioritized_missing and "household_contacts_affected" in prioritized_missing:
                ask = "Have you had any fever or chills, and has anyone else in your home had similar symptoms?"
            elif "has_fever" in prioritized_missing:
                ask = "Have you developed any fever, chills, or felt unwell along with this?"
            elif "household_contacts_affected" in prioritized_missing:
                ask = "Does anyone else in your household or close family have similar skin symptoms?"
            else:
                next_slot = prioritized_missing[0]
                ask = QUESTIONS_EN.get(next_slot, "Could you describe more details about this?")

        full_msg = f"{ack} {ask}".strip() if ack else ask
        return sanitize_safety_constraints(full_msg)

    def _extract_slots(self, utterance: str, slots: ClinicalIntakeSlots, lang: str, last_question_slot: Optional[str] = None) -> None:
        # 1. Primary: Semantic LLM extraction (natural clinical comprehension without brittle pattern matching)
        if self.llm_adapter:
            try:
                system_prompt = (
                    "You are a clinical dermatology intake assistant. Extract clinical history slots from the patient's utterance into structured JSON.\n"
                    "Allowed body_site categories: ['arms', 'legs', 'face', 'hands', 'groin', 'torso', 'whole_body']. Map specific areas naturally (e.g. underarms -> arms, feet/toes -> legs, belly -> torso).\n"
                    "Slots to return:\n"
                    "- body_site: string or null\n"
                    "- lesion_type: string (morphological description in patient's own words, e.g. 'rough and flaky skin', 'dark skin', 'pimples') or null\n"
                    "- duration_days: integer (approximate days, e.g. 1 year = 365, 2 weeks = 14) or null\n"
                    "- has_itching: boolean or null\n"
                    "- has_fever: boolean or null\n"
                    "- household_contacts_affected: boolean or null\n"
                    "- is_spreading: boolean or null\n"
                    "- has_pain: boolean or null\n"
                    f"Context: The last question asked to the patient was about slot '{last_question_slot}'."
                )
                user_prompt = f"Patient Utterance: \"{utterance}\""
                llm_res = self.llm_adapter.generate_json(system_prompt, user_prompt)
                if isinstance(llm_res, dict) and llm_res.get("status") != "fallback":
                    if not slots.body_site and llm_res.get("body_site"):
                        slots.body_site = str(llm_res["body_site"]).lower()
                    if not getattr(slots, "lesion_type", None) and llm_res.get("lesion_type"):
                        slots.lesion_type = str(llm_res["lesion_type"]).lower()
                    if slots.duration_days is None and llm_res.get("duration_days") is not None:
                        try:
                            slots.duration_days = int(llm_res["duration_days"])
                        except (ValueError, TypeError):
                            pass
                    if slots.has_itching is None and llm_res.get("has_itching") is not None:
                        slots.has_itching = bool(llm_res["has_itching"])
                    if slots.has_fever is None and llm_res.get("has_fever") is not None:
                        slots.has_fever = bool(llm_res["has_fever"])
                    if slots.household_contacts_affected is None and llm_res.get("household_contacts_affected") is not None:
                        slots.household_contacts_affected = bool(llm_res["household_contacts_affected"])
                    if slots.is_spreading is None and llm_res.get("is_spreading") is not None:
                        slots.is_spreading = bool(llm_res["is_spreading"])
                    if slots.has_pain is None and llm_res.get("has_pain") is not None:
                        slots.has_pain = bool(llm_res["has_pain"])
            except Exception:
                pass

        lower = utterance.lower()

        is_affirmative = bool(re.search(r'\b(yes|yeah|yep|yup|haan|हाँ|ha|sure|true|correct|affected)\b', lower))
        is_negative = bool(re.search(r'\b(no|nope|nah|nahi|नहीं|nahin|not|nobody|none|never)\b', lower))

        # Contextual resolution if user directly answers the previous question
        if last_question_slot:
            if last_question_slot == "has_fever" and slots.has_fever is None:
                if is_affirmative and not is_negative:
                    slots.has_fever = True
                elif is_negative and not is_affirmative:
                    slots.has_fever = False
            elif last_question_slot == "household_contacts_affected" and slots.household_contacts_affected is None:
                if is_affirmative and not is_negative:
                    slots.household_contacts_affected = True
                elif is_negative and not is_affirmative:
                    slots.household_contacts_affected = False
            elif last_question_slot == "has_itching" and slots.has_itching is None:
                if is_affirmative and not is_negative:
                    slots.has_itching = True
                elif is_negative and not is_affirmative:
                    slots.has_itching = False

        # A. Comprehensive Body Site Extraction
        sites_map = {
            "groin": {
                "en": [
                    r"\bgroin\b", r"\bgenitals?\b", r"\bpubic\b", r"\bprivate parts?\b",
                    r"\bprivate\s+area\b", r"\bdown\s+there\b", r"\bbikini\s+area\b",
                    r"\bperineum\b", r"\bbetween\s+(?:my\s+)?legs\b"
                ],
                "hi": ["गुप्तांग", "जांघ के बीच", "nichla hissa", "janana ang", "neeche", "jangho ke beech"]
            },
            "legs": {
                "en": [
                    r"\blegs?\b", r"\bfeet\b", r"\bfoot\b", r"\bankles?\b", r"\btoes?\b",
                    r"\bcal(?:f|ves)\b", r"\bthighs?\b", r"\bknees?\b", r"\bshins?\b",
                    r"\bheels?\b", r"\bsoles?\b", r"\binner\s+thighs?\b", r"\bbetween\s+(?:my\s+)?toes\b"
                ],
                "hi": [
                    "पैर", "पैरों", "टांग", "टांगों", "घुटना", "घुटनों", "जांघ", "जांघों",
                    "पिंडली", "टखना", "तलवा", "एड़ी", "pairo", "pairoh", "pair",
                    "ungliyon ke beech", "tattiyon", "jangh"
                ]
            },
            "hands": {
                "en": [
                    r"\bhands?\b", r"\bfingers?\b", r"\bpalms?\b", r"\bwrists?\b",
                    r"\bwebs?\b", r"\bknuckles?\b", r"\bnails?\b",
                    r"\bbetween\s+(?:my\s+)?fingers\b", r"\bweb\s*spaces?\b"
                ],
                "hi": ["हाथ", "हाथों", "उंगली", "उंगलियों", "कलाई", "हथेली", "haath", "hath", "anguli", "anguliyon", "nakhun"]
            },
            "arms": {
                "en": [
                    r"\barms?\b", r"\belbows?\b", r"\bforearms?\b", r"\bbiceps?\b",
                    r"\bshoulders?\b", r"\barmpits?\b", r"\bunderarms?\b", r"\bupper\s+arms?\b"
                ],
                "hi": ["बाजू", "बांह", "कोहनी", "कंधा", "कंधे", "बगल", "कांख", "kandha"]
            },
            "face": {
                "en": [
                    r"\bface\b", r"\bcheeks?\b", r"\bforehead\b", r"\bchin\b",
                    r"\bnose\b", r"\blips?\b", r"\bmouth\b", r"\bears?\b",
                    r"\bscalp\b", r"\bhead\b", r"\bnecks?\b", r"\bthroat\b",
                    r"\bhairline\b", r"\bnape\b", r"\bbehind\s+(?:my\s+)?ears?\b",
                    r"\bjaw(?:line)?\b", r"\btemples?\b", r"\beyelids?\b"
                ],
                "hi": [
                    "चेहरा", "चेहरे", "गाल", "माथा", "नाक", "होंठ", "मुंह", "कान", "सिर", "गर्दन", "गला",
                    "chehra", "gardan", "jawline", "thodi", "palakon", "kaanon ke peeche"
                ]
            },
            "torso": {
                "en": [
                    r"\bchest\b", r"\bback\b", r"\bbelly\b", r"\bstomach\b",
                    r"\bwaist\b", r"\babdomen\b", r"\bribs?\b", r"\bbuttocks?\b",
                    r"\bbutt\b", r"\bhips?\b", r"\bnavel\b", r"\bbelly\s*button\b",
                    r"\blower\s+back\b", r"\bupper\s+back\b", r"\bsides?\b", r"\bflanks?\b", r"\btailbone\b"
                ],
                "hi": ["छाती", "सीना", "पीठ", "पेट", "कमर", "कूल्हे", "नितंब", "peeth", "pet", "kamar", "naabhi", "dhundhi", "pasli"]
            }
        }
        if not slots.body_site:
            for site_name, spec in sites_map.items():
                if any(re.search(p, lower) for p in spec["en"]) or any(w in lower for w in spec["hi"]):
                    slots.body_site = site_name
                    break
            if not slots.body_site:
                if any(w in lower for w in [
                    "body", "skin", "everywhere", "all over", "whole body", "full body", "spreading", "spread",
                    "शरीर", "त्वचा", "हर जगह", "पूरे शरीर"
                ]):
                    slots.body_site = "whole_body"

        # B. Comprehensive Duration in Days
        if slots.duration_days is None:
            match_years = re.search(r'(\d+)\s*(?:years?|saal|साल)', lower)
            match_weeks = re.search(r'(\d+)\s*(?:weeks?|हफ्ते|हफ़्ते|सप्ताह|haf?te)', lower)
            match_days = re.search(r'(\d+)\s*(?:days?|दिन|din)', lower)
            match_months = re.search(r'(\d+)\s*(?:months?|महीने|माह|mahine)', lower)

            if match_years:
                slots.duration_days = int(match_years.group(1)) * 365
            elif match_weeks:
                slots.duration_days = int(match_weeks.group(1)) * 7
            elif match_days:
                slots.duration_days = int(match_days.group(1))
            elif match_months:
                slots.duration_days = int(match_months.group(1)) * 30
            elif any(w in lower for w in ["a year", "an year", "one year", "1 year", "ek saal", "एक साल"]):
                slots.duration_days = 365
            elif any(w in lower for w in ["two weeks", "दो हफ्ते", "2 weeks", "2 hafte"]):
                slots.duration_days = 14
            elif any(w in lower for w in ["one week", "एक हफ्ता", "1 week", "a week", "1 hafta"]):
                slots.duration_days = 7
            elif any(w in lower for w in ["today", "आज", "yesterday", "कल", "since yesterday", "last night"]):
                slots.duration_days = 1
            elif any(w in lower for w in ["few days", "कुछ दिन", "couple of days", "kuch din"]):
                slots.duration_days = 3
            elif any(w in lower for w in ["since childhood", "all my life", "born with it", "bachpan se", "bachpan", "पैदाइशी", "बचपन से"]):
                slots.duration_days = 3650
            elif any(w in lower for w in ["on and off", "comes and goes", "recurrent", "recurring", "aata jaata", "aata hai jaata hai", "बार-बार"]):
                slots.duration_days = 90
            elif any(w in lower for w in ["seasonal", "worse in winter", "worse in summer", "sardi me", "garmi me", "मौसमी"]):
                slots.duration_days = 180
            elif any(w in lower for w in ["last month", "past month", "pichle mahine", "पिछले महीने"]):
                slots.duration_days = 30
            elif any(w in lower for w in ["last year", "pichle saal", "पिछले साल", "past year"]):
                slots.duration_days = 365
            elif any(w in lower for w in ["long time", "bahut din", "bahut samay", "बहुत दिन", "kaafi time"]):
                slots.duration_days = 60
            elif any(w in lower for w in ["recently", "haal hi mein", "हाल ही में", "just started"]):
                slots.duration_days = 3

        # C. Comprehensive Itching
        if slots.has_itching is None:
            if any(w in lower for w in [
                "खुजली नहीं", "no itch", "does not itch", "doesn't itch", "not itchy", "no itching",
                "not achieved", "notes on teaching", "no itching at all", "khujli nahi"
            ]):
                slots.has_itching = False
            elif any(w in lower for w in ["खुजली", "itching", "itch", "itchy", "खजुलाहट", "scratch", "scratching", "khujli", "khujali"]):
                slots.has_itching = True
            elif "yes" in lower and slots.body_site and slots.duration_days is not None:
                slots.has_itching = True

        # D. Comprehensive Fever
        if slots.has_fever is None:
            if any(w in lower for w in ["बुखार नहीं", "no fever", "no temperature", "no chills", "without fever", "bukhar nahi"]):
                slots.has_fever = False
            elif any(w in lower for w in ["बुखार", "fever", "shivering", "chills", "तप रहा", "temperature", "bukhar"]):
                slots.has_fever = True

        # E. Comprehensive Household Contacts
        if slots.household_contacts_affected is None:
            # Check negation first (nobody, alone, only me, nobody else)
            if any(w in lower for w in [
                "nobody in my family", "no one in my family", "nobody else", "no one else",
                "only me", "just me", "alone", "किसी को नहीं", "no one", "kisi ko nahi", "sirf mujhe"
            ]):
                slots.household_contacts_affected = False
            elif any(w in lower for w in [
                "brother", "sister", "family", "mother", "father", "roommate", "partner", "wife", "husband",
                "kid", "kids", "घर में", "भाई", "बहन", "परिवार", "सबको", "bhai", "behen", "ghar me"
            ]):
                # Make sure it's not negated with 'no'
                if not any(neg in lower for neg in ["nobody", "no one", "nahi", "not"]):
                    slots.household_contacts_affected = True

        # E2. Symptom Qualifiers (spreading, pain)
        if slots.is_spreading is None:
            if any(w in lower for w in ["spreading", "getting bigger", "growing", "increasing", "expanding", "phail raha", "badh raha", "फैल रहा", "बढ़ रहा"]):
                slots.is_spreading = True
            elif any(w in lower for w in ["same size", "not spreading", "stable", "nahi phail raha", "नहीं फैल रहा"]):
                slots.is_spreading = False

        if slots.has_pain is None:
            if any(w in lower for w in ["pain", "painful", "hurts", "sore", "tender", "dard", "dard ho raha", "दर्द", "दर्दनाक", "takleef"]):
                slots.has_pain = True
            elif any(w in lower for w in ["no pain", "painless", "not painful", "dard nahi", "दर्द नहीं"]):
                slots.has_pain = False

        # F. Age
        if slots.age is None:
            age_match = re.search(r'\b(?:age|उम्र|आयु)\s*(?:is|of|hai)?\s*(\d{1,2})\b|\b(\d{1,2})\s*(?:years\s*old|साल\s*की|साल\s*का)\b', lower)
            if age_match:
                try:
                    val_str = age_match.group(1) or age_match.group(2)
                    if val_str:
                        val = int(val_str)
                        if 1 <= val <= 100:
                            slots.age = val
                except ValueError:
                    pass

        # G. Lesion Morphology / Complaint Description
        if not getattr(slots, "lesion_type", None):
            morphology_patterns = [
                (r"\b(sores?|ulcers?|open wounds?|wound)\b", "sores/ulcers"),
                (r"\b(warts?|verruca|skin tags?|growths?)\b", "warts/growths"),
                (r"\b(crusting|crusty|scab(?:bing)?|scabs?)\b", "crusting/scabs"),
                (r"\b(oozing|weeping|leaking fluid|discharge|pus)\b", "oozing/discharge"),
                (r"\b(bleeding|blood|bleeds?)\b", "bleeding"),
                (r"\b(thickened skin|thickening|hardened skin|rough patches?)\b", "thickened/rough skin"),
                (r"\b(discoloration|discolored|skin (?:getting|turning) (?:dark|light|white)|white (?:spots?|patches?)|dark (?:spots?|patches?))\b", "discoloration/pigment changes"),
                (r"\b(stretch marks?|striae)\b", "stretch marks"),
                (r"\b(ringworm|ring-like|circular ring)\b", "ringworm/ring-shaped"),
                (r"\b(dandruff|flakes on scalp|scalp flaking)\b", "dandruff/scalp flaking"),
                (r"\b(fungal|fungus|athletes? foot|jock itch)\b", "fungal infection"),
                (r"\b(nail (?:infection|fungus|discoloration|thickening|yellowing))\b", "nail problem"),
                (r"\b(rough and flaky(?: skin)?|flaky and rough(?: skin)?)\b", "rough and flaky skin"),
                (r"\b(rough(?: skin)?|flaky(?: skin)?|peeling(?: skin)?|dry and scaly|scaly and dry)\b", "rough and flaky skin"),
                (r"\b(dry skin|dryness|flakiness|cracked skin)\b", "dry and flaky skin"),
                (r"\b(pimples?|acne|breakouts?|zits?|blackheads?|whiteheads?)\b", "acne/breakouts"),
                (r"\b(blisters?|boils?|small bumps?|fluid-filled bumps?|red bumps?|bumps?)\b", "bumps/blisters"),
                (r"\b(dark spots?|black spots?|brown spots?|pigmented spots?|moles?)\b", "dark spot/mole"),
                (r"\b(hives|welts?|swelling|allergic reaction|swollen patches?)\b", "hives/swelling"),
                (r"\b(scaly patches?|red patches?|dry patches?|circular patches?|patches?)\b", "scaly patches"),
                (r"\b(burning sensation|burning skin|irritation|redness)\b", "skin irritation/redness"),
                (r"\b(rashes?|rash)\b", "rash"),
            ]
            for pat, desc in morphology_patterns:
                if re.search(pat, lower):
                    slots.lesion_type = desc
                    break

            if not getattr(slots, "lesion_type", None):
                # Hinglish / Romanized Hindi patterns
                hinglish_morphology = [
                    (r"\b(daad|ringworm)\b", "ringworm/ring-shaped"),
                    (r"\b(phunsi|phunsiya|phunsiyan|muhase|muhasa)\b", "acne/breakouts"),
                    (r"\b(massa|masse|skin tag)\b", "warts/growths"),
                    (r"\b(papdi|khurand)\b", "crusting/scabs"),
                    (r"\b(mavad|peep|pus)\b", "oozing/discharge"),
                    (r"\b(chaale|chhaale|faphola|faphole)\b", "bumps/blisters"),
                    (r"\b(rusi|dandruff)\b", "dandruff/scalp flaking"),
                    (r"\b(safed daag|kala daag|daag)\b", "discoloration/pigment changes"),
                ]
                for pat, desc in hinglish_morphology:
                    if re.search(pat, lower):
                        slots.lesion_type = desc
                        break

            if not getattr(slots, "lesion_type", None):
                morphology_patterns_hi = [
                    (["घाव", "छाला", "ज़ख़्म", "नासूर"], "घाव/छाला"),
                    (["मस्सा", "मस्से", "स्किन टैग"], "मस्सा/स्किन टैग"),
                    (["पपड़ी", "खुरंड"], "पपड़ी/खुरंड"),
                    (["रिसना", "मवाद", "पीप", "पस"], "मवाद/रिसाव"),
                    (["खून", "खून आना", "खून निकलना"], "खून बहना"),
                    (["दाद", "गोल चकत्ता", "रिंगवर्म"], "दाद/रिंगवर्म"),
                    (["रूसी", "सिर में रूसी", "रूसी उड़ना"], "रूसी"),
                    (["सफ़ेद दाग", "सफेद धब्बे", "रंग बदलना", "काले धब्बे"], "रंग बदलना"),
                    (["रूखी और पपड़ीदार", "पपड़ीदार और रूखी", "रूखी त्वचा", "पपड़ीदार त्वचा", "फटी त्वचा", "सूखी त्वचा"], "रूखी और पपड़ीदार त्वचा"),
                    (["मुंहासे", "मुहासे", "फुंसी", "फुंसियां", "पिंपल", "पिंपल्स"], "मुंहासे/फुंसियां"),
                    (["काला तिल", "काला धब्बा", "काला दाग", "तिल"], "काला तिल/धब्बा"),
                    (["दाने", "फफोले", "छाले", "लाल दाने"], "दाने/फफोले"),
                    (["पित्ती", "सूजन", "उभरे हुए चकत्ते"], "पित्ती/सूजन"),
                    (["चकत्ते", "चकत्ता", "लाल चकत्ते"], "चकत्ते"),
                    (["जलन", "लालपन"], "त्वचा की जलन")
                ]
                for terms, desc_hi in morphology_patterns_hi:
                    if any(w in lower for w in terms):
                        slots.lesion_type = desc_hi
                        break

    def _build_confirmation_prompt(self, slots: ClinicalIntakeSlots, lang: str) -> str:
        site = slots.body_site or ("त्वचा" if lang == "hi" else "skin")
        days = slots.duration_days or 7
        duration_str = f"{days} days" if lang == "en" else f"{days} दिन"
        if days >= 7 and days % 7 == 0:
            weeks = days // 7
            duration_str = f"{weeks} week{'s' if weeks > 1 else ''}" if lang == "en" else f"{weeks} हफ्ते"

        itch_str = ("खुजली के साथ" if lang == "hi" else "with itching") if slots.has_itching else ("बिना खुजली के" if lang == "hi" else "without itching")
        problem_desc = getattr(slots, "lesion_type", None) or ("त्वचा की समस्या" if lang == "hi" else "skin issue")

        if lang == "hi":
            return f"मैंने दर्ज कर लिया है: आपके {site} पर {duration_str} से {problem_desc} {itch_str}।"
        else:
            return f"I have recorded: {problem_desc} on your {site} for {duration_str} {itch_str}."
