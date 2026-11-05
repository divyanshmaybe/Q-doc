"""
Two-Tier Clinical Agent Architecture for Q-Doc MVP.

Tier 1: Utterance Normalizer & Intent Resolver (Fast LLM)
- Repairs speech-to-text acoustic artifacts (e.g. "not achieved" -> "not itchy", "notes on teaching" -> "no itching")
- Interprets user meaning, language nuances, colloquialisms, and temporal expressions
- Outputs clean normalized clinical intent and extracted semantic entities

Tier 2: Head Dermatologist Agent (Knowledge-Grounded Clinical Brain)
- Maintains persistent back-memory of patient state and history
- Queries deep clinical dermatology knowledge base (IADVL, AAD, BAD)
- Dynamically plans what information is still missing to formulate a differential
- Formulates empathetic, clinically intelligent questions (or photo readiness confirmation)
- Adheres strictly to non-prescriptive safety constraints
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from services.dialogue.schemas import ClinicalIntakeSlots, SkinCondition
from services.clinical_knowledge.dermatology_kb import DermatologyKnowledgeService
from services.gateway.llm import LLMAdapter
from services.policy.rules import sanitize_safety_constraints
from services.tools.web_search import MedicalWebSearchTool


class UtteranceNormalizer:
    """Tier 1: Fixes STT slips, repairs phonetic mishearings, and extracts intent."""
    def __init__(self, llm_adapter: Optional[LLMAdapter] = None):
        self.llm = llm_adapter or LLMAdapter()

    def normalize(
        self,
        raw_transcript: str,
        last_agent_question: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Uses fast LLM to repair phonetic STT slips and extract semantic intent.
        Returns normalized patient statement and any directly identifiable slots.
        """
        system_prompt = (
            "You are a medical speech-to-text normalization engine for a dermatology assistant.\n"
            "Raw patient audio transcripts often have phonetic mistakes, speech recognizer errors, "
            "slang, or mixed Hindi/Hinglish/English grammar (e.g. 'not achieved' instead of 'not itchy', "
            "'notes on teaching' instead of 'no itching', '1 year' instead of days).\n\n"
            "Tasks:\n"
            "1. Fix the transcript into what the patient actually meant to say (clean_meaning).\n"
            "2. Extract clinical entities if present: body_site, lesion_type, duration_days, has_itching, has_fever, household_contacts_affected, has_pain, is_spreading.\n"
            f"Context: The agent just asked the patient: \"{last_agent_question or 'Initial complaint'}\".\n\n"
            "Return JSON ONLY with this schema:\n"
            "{\n"
            '  "clean_meaning": "string (what the user intended)",\n'
            '  "detected_language": "en" or "hi",\n'
            '  "body_site": "arms"|"legs"|"face"|"hands"|"groin"|"torso"|"whole_body"|null,\n'
            '  "lesion_type": "string (patient description)"|null,\n'
            '  "duration_days": integer|null,\n'
            '  "has_itching": true|false|null,\n'
            '  "has_fever": true|false|null,\n'
            '  "household_contacts_affected": true|false|null,\n'
            '  "has_pain": true|false|null,\n'
            '  "is_spreading": true|false|null\n'
            "}"
        )

        user_prompt = f"Raw Transcript: \"{raw_transcript}\""
        try:
            res = self.llm.generate_json(system_prompt, user_prompt)
            if isinstance(res, dict) and res.get("status") != "fallback":
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
    """
    Tier 2: Master Clinical Dermatologist Agent with vast knowledge base grounding
    and dynamic, condition-tailored differential inquiry.
    
    NO QUESTIONING CAP: The agent is permitted to inquire as many times as necessary
    until it is confident in the clinical condition. It is never prematurely capped.
    """
    def __init__(self, llm_adapter: Optional[LLMAdapter] = None, max_turns: Optional[int] = None):
        self.llm = llm_adapter or LLMAdapter()
        self.max_turns = max_turns
        self.search_tool = MedicalWebSearchTool()

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
        slots.turn_count += 1
        is_hi = lang.startswith("hi")

        # 1. Update Back-Memory with clinical entities
        for field in [
            "body_site", "lesion_type", "duration_days", "has_itching",
            "has_fever", "household_contacts_affected", "has_pain", "is_spreading"
        ]:
            val = normalized_intent.get(field)
            if val is not None and getattr(slots, field, None) is None:
                setattr(slots, field, val)

        # Store any freeform condition-specific cues into condition_specific_history
        meaning = normalized_intent.get("clean_meaning", "").lower()
        if any(w in meaning for w in ["weight", "gain", "fat", "obese", "sugar", "diabetes", "insulin", "pcod", "pcos"]):
            slots.condition_specific_history["metabolic_clues"] = meaning
        if any(w in meaning for w in ["velvet", "thick", "rough", "pumice", "scrub"]):
            slots.condition_specific_history["texture_clues"] = meaning
        if any(w in meaning for w in ["joint", "knee", "elbow", "scale", "silver"]):
            slots.condition_specific_history["psoriasis_clues"] = meaning
        if any(w in meaning for w in ["pet", "cat", "dog", "gym", "towel", "ring"]):
            slots.condition_specific_history["fungal_clues"] = meaning

        # 2. Retrieve targeted knowledge references based on current complaint
        clinical_context = self._get_relevant_knowledge(slots)

        has_photo = bool(slots.photo_image_id)
        photo_morphology = slots.condition_specific_history.get("visual_findings") or slots.condition_specific_history.get("visual_morphology", "")

        known_summary = {
            "body_site": slots.body_site,
            "lesion_type": slots.lesion_type,
            "duration_days": slots.duration_days,
            "has_itching": slots.has_itching,
            "has_fever": slots.has_fever,
            "household_contacts_affected": slots.household_contacts_affected,
            "has_photo_uploaded": has_photo,
            "photo_visual_morphology": photo_morphology,
            "condition_specific_history": slots.condition_specific_history,
            "suspected_differentials": slots.suspected_differentials,
            "primary_suspected_condition": slots.primary_suspected_condition
        }

        # 3. Dynamic Clinical Differential Reasoner Prompt
        system_prompt = (
            "You are a Senior Consultant Dermatologist conducting an empathetic, intelligent clinical consultation.\n"
            "You have access to an extensive dermatology clinical knowledge base (IADVL, AAD, BAD) and web search guidelines.\n\n"
            "CLINICAL CONSULTATION SEQUENCE:\n"
            "1. EARLY PHOTO INTAKE (After turn 1 or 2):\n"
            "   - If the patient has not yet provided a photo (has_photo_uploaded is false) and body_site/complaint is known:\n"
            "     Invite them to take a photo now so you can inspect visual patterns first: set 'ready_for_photo': true.\n"
            "     Spoken question: Acknowledge what they shared and ask for a clear photo of the lesion to guide targeted questions.\n"
            "2. POST-PHOTO INVESTIGATION & NO QUESTIONING CAP:\n"
            "   - If a photo has already been uploaded (has_photo_uploaded is true):\n"
            "     Evaluate the photo's visual morphology alongside the patient's responses.\n"
            "     Identify 3 to 5 candidate differentials (e.g. Acanthosis Nigricans, Scabies, Eczema, Psoriasis, Tinea, Vitiligo, Melasma, Rosacea, etc.).\n"
            "     Ask targeted, condition-specific discriminating questions to confirm the diagnosis (e.g., for Acanthosis Nigricans: ask about velvety texture, weight changes, diabetes/insulin resistance; for Scabies: nocturnal itch surge & household contacts; for Psoriasis: silvery micaceous scale & joint pains).\n"
            "     You are permitted to ask AS MANY QUESTIONS AS NEEDED until you have clinical certainty. There is NO cap.\n"
            "3. FINAL VERDICT & CARE PLAN:\n"
            "   - When you have sufficient clinical certainty (diagnostic_confidence >= 0.80 or key discriminating clues answered):\n"
            "     Set 'ready_for_verdict': true.\n"
            "     In 'agent_question', deliver the complete clinical verdict: the confirmed diagnosis, the underlying mechanism/cause, first-line evidence-based active ingredients/lotions, daily hygiene protocol, and clinical red flags.\n"
            "4. SAFETY CONSTRAINTS:\n"
            "   - Common benign conditions must receive direct provisional diagnosis and self-care plans. Only refer to doctor for true red flags (malignancy, rapid spreading rash with fever).\n"
            "   - NEVER prescribe drugs with exact dosages (e.g. no '500mg' or 'twice daily'). Keep language warm and natural.\n"
            f"Target Language: {'Hindi (Devanagari or natural Hindustani)' if is_hi else 'Clear Indian English'}"
        )

        user_prompt = f"""Patient Case State in Back Memory:
{json.dumps(known_summary, indent=2)}

Patient's Latest Intended Message: "{normalized_intent.get('clean_meaning', '')}"
Clinical Guidance / Differential Hints: {clinical_context}
Turn Count: {slots.turn_count}

Analyze the case and return JSON ONLY with this schema:
{{
  "suspected_differentials": ["candidate condition 1", "candidate condition 2", "candidate condition 3"],
  "primary_suspected_condition": "leading condition name or null",
  "diagnostic_confidence": 0.0 to 1.0,
  "ready_for_photo": true or false,
  "ready_for_verdict": true or false,
  "agent_question": "Spoken response to patient (if ready_for_photo is true, invite photo; if ready_for_verdict is true, give diagnosis and full self-care plan; otherwise ask the next condition-specific discriminating question)"
}}"""

        try:
            res = self.llm.generate_json(system_prompt, user_prompt)
            if isinstance(res, dict) and res.get("agent_question"):
                differentials = res.get("suspected_differentials", [])
                if differentials:
                    slots.suspected_differentials = differentials
                if res.get("primary_suspected_condition"):
                    slots.primary_suspected_condition = res["primary_suspected_condition"]
                slots.diagnostic_confidence = float(res.get("diagnostic_confidence", 0.5))

                ready_photo = bool(res.get("ready_for_photo", False))
                # Trigger early photo after turn 1 if site is known and photo not yet captured
                if not has_photo and slots.body_site and slots.turn_count >= 1:
                    ready_photo = True

                ready_verdict = bool(res.get("ready_for_verdict", False)) or (has_photo and slots.diagnostic_confidence >= 0.80)

                # Cap override if explicitly configured
                if self.max_turns is not None and slots.turn_count >= self.max_turns:
                    ready_verdict = True

                agent_msg = res["agent_question"].strip()
                slots.is_ready_for_photo = ready_photo
                slots.is_final_verdict_ready = ready_verdict
                slots.is_complete = ready_photo or ready_verdict

                confirm_prompt = None
                if ready_photo and not has_photo:
                    dur_str = f"{slots.duration_days} days" if slots.duration_days else "several days"
                    site = slots.body_site or "affected area"
                    cond = slots.primary_suspected_condition or getattr(slots, "lesion_type", "") or "condition"
                    confirm_prompt = (
                        f"मैंने दर्ज किया है: {site} पर {cond} ({dur_str})।" if is_hi else
                        f"Recorded: {cond} on your {site} ({dur_str})."
                    )

                return slots, sanitize_safety_constraints(agent_msg), ready_photo or ready_verdict, confirm_prompt
        except Exception as e:
            print(f"[HeadDermatologistAgent] LLM reasoning error: {e}")

        # Intelligent Fallback if LLM unavailable
        site = (slots.body_site or "").lower()
        meaning = normalized_intent.get("clean_meaning", "").lower()
        if not has_photo:
            ask = (
                f"मैंने आपके {site or 'त्वचा'} पर परेशानी को नोट कर लिया है। कृपया इस हिस्से की एक साफ फोटो लें ताकि मैं इसे देखकर सही सवाल पूछ सकूं।" if is_hi else
                f"I've noted the issue on your {site or 'skin'}. Please take a clear photo of the area right now so I can inspect it directly and ask targeted questions."
            )
            slots.is_ready_for_photo = True
            slots.is_complete = True
            return slots, sanitize_safety_constraints(ask), True, f"Recorded symptoms on {site or 'skin'}."
        elif any(w in site for w in ["arm", "neck", "underarm", "axilla"]) or "dark" in meaning:
            ask = (
                "क्या यह त्वचा छूने में मखमली या मोटी लगती है, और क्या वजन या शुगर में कोई बदलाव आया है?" if is_hi else
                "Does the darkened skin feel slightly velvety or thickened to the touch, and have you noticed any recent changes in weight or blood sugar?"
            )
        elif slots.has_itching:
            ask = (
                "क्या रात में खुजली बहुत ज्यादा बढ़ जाती है, या घर में किसी और को भी ऐसी परेशानी है?" if is_hi else
                "Does the itching become significantly worse at night, or has anyone else at home had similar symptoms?"
            )
        else:
            ask = (
                "क्या इस हिस्से में कोई पपड़ी, दाने या लालिमा है?" if is_hi else
                "Are there any flakes, scaling, or redness in this area?"
            )

        agent_msg = f"{ask}"
        ready = bool(slots.diagnostic_confidence >= 0.80)
        slots.is_complete = ready
        return slots, sanitize_safety_constraints(agent_msg), ready, None

    def _get_relevant_knowledge(self, slots: ClinicalIntakeSlots) -> str:
        """Pulls condition-specific differential guidance from the Dermatology Knowledge Base and Web Search."""
        hints = []
        site = (slots.body_site or "").lower()
        lesion = (slots.lesion_type or "").lower()

        if any(w in site for w in ["arm", "underarm", "neck", "axilla"]) or "dark" in lesion:
            hints.append("Acanthosis Nigricans (L83): Velvety hyperpigmentation in flexural creases; strongly linked to insulin resistance, obesity, PCOD. Distinguish from PIH and Tinea Versicolor.")
        if any(w in site for w in ["finger", "wrist", "web", "hand"]) or slots.has_itching:
            hints.append("Scabies (B86): Nocturnal pruritus surge; interdigital burrows; household clustering. Distinguish from Dyshidrotic Eczema.")
        if "groin" in site:
            hints.append("Tinea Cruris (B35.6): Annular raised scaly active border with central clearing in inguinal folds.")
        if any(w in site for w in ["elbow", "knee", "scalp"]) or "scale" in lesion or "plaque" in lesion:
            hints.append("Psoriasis Vulgaris (L40): Well-demarcated erythematous plaques with silvery micaceous scales.")
        if not hints:
            hints.append("Broad primary care clinical differential screening protocol.")

        # Real-time web search retrieval for specific uncommon symptoms or presentations
        if lesion and len(lesion) > 3:
            try:
                web_hits = self.search_tool.search_clinical_guidelines(f"{site} {lesion}", max_results=1)
                for h in web_hits:
                    if h.get("snippet"):
                        hints.append(f"Web Reference ({h['title']}): {h['snippet'][:120]}...")
            except Exception:
                pass

        return " | ".join(hints)

