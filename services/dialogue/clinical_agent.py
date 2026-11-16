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
            "Extract only facts explicitly stated in the patient's transcript. Never invent or repair clinical meaning. "
            "Preserve negation, numbers, units and uncertainty. If speech is ambiguous, leave that field null "
            "and add its name to ambiguous_fields with ambiguity_evidence mapping the field to an exact ambiguous quote from this transcript. Missing or unmentioned facts are NOT ambiguous. A short yes/no answers the previous question only; do not mark unrelated fields ambiguous. Do not reinterpret a year as days or unclear words as no itching. "
            "Include ambiguity_evidence as an object of field: verbatim quote. "
            "Return JSON: clean_meaning (verbatim transcript), detected_language (en/hi), ambiguous_fields (list), "
            "body_site, lesion_type, duration_days, age, has_itching, has_fever, has_pain, is_spreading, "
            "household_contacts_affected, breathing_difficulty, mucosal_involvement, is_pregnant, "
            "patient_concern, daily_impact, prior_treatments, treatment_barriers, nocturnal_itch, triggers. Unknown values must be null. Itching does not mean no pain. Never infer a symptom is absent because another symptom is reported. Pronouns refer to the already discussed problem; they do not make its location ambiguous. "
            f"Previous question: {last_agent_question or 'Initial complaint'}. Language: {language}."
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
