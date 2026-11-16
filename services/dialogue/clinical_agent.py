"""Explicit-fact extraction and consultation planner compatibility adapter."""

from typing import Dict, Any, List, Optional, Tuple
from services.dialogue.schemas import ClinicalIntakeSlots
from services.gateway.llm import LLMAdapter


class UtteranceNormalizer:
    """Tier 1: Extracts explicit facts and flags uncertain speech for clarification."""
    def __init__(self, llm_adapter: Optional[LLMAdapter] = None):
        self.llm = llm_adapter or LLMAdapter()

    def normalize(
        self,
        raw_transcript: str,
        last_agent_question: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Uses an LLM to extract explicit facts without rewriting clinical meaning.
        Returns normalized patient statement and any directly identifiable slots.
        """
        system_prompt = (
            "You are an expert dermatological clinical intake intelligence. "
            "Your task is to deeply understand the patient's conversational transcript in the context of the previous doctor/assistant question. "
            "Never invent facts not stated by the patient. Accurately interpret natural conversational phrasing, negations, temporal units, and anatomical locations.\n\n"
            "Extract and return a JSON object with the following fields:\n"
            "- clean_meaning: string (the verbatim patient statement)\n"
            "- detected_language: 'en' or 'hi'\n"
            "- safety_screen_complete: boolean or null. Set true if the patient answers and denies the dangerous red-flag screening questions (e.g. confirms NO trouble breathing, NO sores in mouth or eyes, NO skin peeling, or general negative phrases like 'none', 'nothing like that', 'there was no trouble breathing', 'no I don't have those'). Set false if they report any of these dangerous symptoms. Set null if the safety screen question was not asked or not answered.\n"
            "- breathing_difficulty: boolean or null. True if patient reports trouble breathing or shortness of breath; false if explicitly denied; null if unmentioned.\n"
            "- mucosal_involvement: boolean or null. True if sores in mouth or eyes, or skin peeling reported; false if explicitly denied; null if unmentioned.\n"
            "- body_site: string or null. The canonical anatomical site of the skin complaint (e.g. 'throat', 'neck', 'hands', 'face', 'legs', 'feet', 'arms', 'back', 'chest', 'groin', 'whole_body'). Understand conversational context accurately without forcing throat or neck into face.\n"
            "- lesion_type: string or null (e.g. 'rash', 'pimples', 'itching', 'bumps', 'dry patch')\n"
            "- duration_days: integer or null. Convert conversational duration to days (e.g. '1 year' -> 365, '2 weeks' -> 14, '5 days' -> 5, '3 months' -> 90).\n"
            "- has_itching: boolean or null. True if itching/scratching reported, false if denied.\n"
            "- has_pain: boolean or null. True if pain/burning reported, false if denied. Note: itching alone does NOT mean no pain.\n"
            "- has_fever: boolean or null. True if fever/chills reported, false if denied.\n"
            "- is_spreading: boolean or null. True if rash is spreading or expanding, false if static or denied.\n"
            "- household_contacts_affected: boolean or null. True if family or household members have similar rash/itch, false if denied.\n"
            "- nocturnal_itch: boolean or null. True if itching gets worse at night, false if not.\n"
            "- is_pregnant: boolean or null\n"
            "- patient_concern: string or null (the patient's primary worry or concern)\n"
            "- daily_impact: string or null (how the condition affects sleep, work, or daily life)\n"
            "- prior_treatments: string or null (creams, medications, or remedies already tried)\n"
            "- triggers: string or null (any triggers noticed by the patient)\n"
            "- treatment_barriers: string or null\n"
            "- summary_confirmed: boolean or null. True if the patient confirms the consultation summary (e.g. 'yes', 'correct', 'that's right', 'all good', 'looks fine'), false if they correct or deny it.\n"
            "- ambiguous_fields: list of field names ONLY if the patient's statement about that specific field is self-contradictory or truly uncertain.\n"
            f"Context: Previous agent question was: \"{last_agent_question or 'Initial complaint'}\". Language: {language}."
        )

        user_prompt = f"Raw Transcript: \"{raw_transcript}\""
        try:
            res = self.llm.generate_json(system_prompt, user_prompt)
            if isinstance(res, dict) and res.get("status") != "fallback":
                # Model uncertainty must be grounded in the current utterance.
                # Absent fields are normal in a multi-turn conversation.
                evidence = res.get("ambiguity_evidence", {})
                if not isinstance(evidence, dict):
                    evidence = {}
                ambiguous = res.get("ambiguous_fields", [])
                if not isinstance(ambiguous, list):
                    ambiguous = []
                res["ambiguous_fields"] = [
                    field for field in ambiguous if isinstance(field, str)
                    and isinstance(evidence.get(field), str)
                    and evidence[field].strip()
                    and evidence[field].strip().casefold() in raw_transcript.casefold()
                ]
                return res
        except Exception:
            pass

        # Fallback to raw text if LLM unavailable
        return {
            "clean_meaning": raw_transcript,
            "detected_language": language,
            "body_site": None,
            "lesion_type": None,
            "duration_days": None,
            "has_itching": None,
            "has_fever": None,
            "household_contacts_affected": None
        }


class HeadDermatologistAgent:
    """Compatibility adapter for the explicit consultation planner."""
    def __init__(self, llm_adapter: Optional[LLMAdapter] = None, max_turns: Optional[int] = None):
        self.llm = llm_adapter or LLMAdapter()
        self.max_turns = max_turns

    def step(
        self,
        slots: ClinicalIntakeSlots,
        normalized_intent: Dict[str, Any],
        turn_history: List[Dict[str, Any]],
        lang: str = "en"
    ) -> Tuple[ClinicalIntakeSlots, str, bool, Optional[str]]:
        """
        Executes a dynamic clinical differential consultation turn.
        """
        from services.dialogue.consultation import ConsultationPlanner
        return ConsultationPlanner(self.llm, self.max_turns).step(
            slots, normalized_intent, turn_history, lang
        )
