"""
Multimodal Dermatologist Agent for Q-Doc MVP.

Directly analyzes patient skin photographs using Multimodal Vision (Gemini 3.1 Flash-Lite)
combined with clinical patient voice intake, local classifier priors, and
real-time medical web search grounding.
"""

import os
import io
import json
import base64
import requests
from services.gateway.llm import post_gemini
from services.gateway.errors import ProviderError
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from PIL import Image

from services.dialogue.schemas import (
    SkinCondition,
    ClinicalIntakeSlots,
    IntakeFacts,
    ImagePrediction,
    ClinicalReasonerOutput,
    DifferentialDiagnosisItem
)
from services.tools.web_search import MedicalWebSearchTool
from services.policy.rules import sanitize_safety_constraints
from services.clinical_knowledge.coverage import catalog_prompt, normalize_condition, get_coverage

load_dotenv()


class MultimodalDermatologistAgent:
    """
    Multimodal Diagnostic AI:
    1. Inspects raw skin photograph pixels directly (lesion morphology, color, border, distribution).
    2. Incorporates patient clinical history (symptom onset, pruritus, contacts, fever).
    3. Leverages MedicalWebSearchTool to fetch real-time clinical guidelines when needed.
    4. Provides comprehensive provisional diagnosis, visual reasoning, differential, and self-care plan.
    """

    def __init__(self, api_key: Optional[str] = None):
        raw_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.gemini_key = raw_key.strip("'\" \t\r\n") if raw_key else ""
        self.search_tool = MedicalWebSearchTool()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    def inspect_early_photo(
        self,
        image_bytes: bytes,
        intake: ClinicalIntakeSlots,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Inspects an early lesion photo captured after 1-2 initial intake turns.
        Forms 3-5 candidate differential hypotheses and formulates the first
        condition-specific discriminating question for the patient.
        """
        is_hi = ("hi" in language.lower()) if language else ("hi" in (intake.primary_language or "").lower())

        if self.gemini_key:
            try:
                # Prepare image
                pil_img = Image.open(io.BytesIO(image_bytes))
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                pil_img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=90)
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

                system_instruction = (
                    "You are a Senior Consultant Multimodal Dermatologist inspecting a patient's skin photograph in a teledermatology consultation.\n"
                    "The patient has shared their opening complaint. Now you are visually inspecting the skin to form 3-5 candidate differential hypotheses "
                    "and formulate a natural, empathetic, doctor-like question specifically tailored to what you see and what the patient has reported.\n\n"
                    "CLINICAL GUIDELINES & PROMPT REFERENCES (Use as clinical guidance, not fixed templates):\n"
                    "1. Directly inspect the lesion morphology (color, pattern, border, elevation, scale, follicular involvement, flexural/extensor distribution).\n"
                    "2. Formulate 3 to 5 candidate differential diagnoses from the provided catalog.\n"
                    "3. Dynamically craft an empathetic, conversational clinical question (2-3 sentences max) tailored to the individual case:\n"
                    "   - Acne / Folliculitis: acknowledge visible comedones/papules/pustules, probe tenderness, oiliness, or shaving/cosmetic triggers.\n"
                    "   - Acanthosis Nigricans: probe velvety/thickened texture, weight changes, or personal/family history of insulin resistance or diabetes.\n"
                    "   - Scabies / Infestations: probe nocturnal itch exacerbation, burrows, and household/close contacts itching.\n"
                    "   - Tinea / Fungal infections: probe active annular/ring borders, central clearing, maceration, sweating, pet contact, or shared items.\n"
                    "   - Psoriasis: probe thick micaceous silvery scaling, extensor distribution, nail pitting, or morning joint stiffness.\n"
                    "   - Eczema / Dermatitis: probe intense pruritus, personal/family atopy history, xerosis, or contact with detergents, chemicals, or metals.\n"
                    "   - Urticaria / Hives: probe whether individual wheals are evanescent (disappearing or moving within 24 hours), and check for allergy/food triggers.\n"
                    "   - Vitiligo / Melasma: probe pigment evolution, sun reactivity, or symmetrical distribution.\n"
                    "   - Lichen Planus: probe polygonal violaceous papules, Wickham striae, or oral/mucosal soreness.\n"
                    "   - Bacterial / Cellulitis / Impetigo: probe rapid spreading warmth, honey-colored crusts, tenderness, or systemic malaise.\n"
                    "   - Other conditions: identify the most discriminating clinical question that a skilled dermatologist would ask to distinguish the diagnosis.\n"
                    "4. STRICT SAFETY GUARDRAILS:\n"
                    "   - NEVER prescribe any medications, brand names, or dosages.\n"
                    "   - NEVER definitively confirm a diagnosis yet; frame questions conversationally to gather more clinical history.\n"
                    f"Target Language: {'Hindi (Devanagari or natural Hindustani)' if is_hi else 'Clear Indian English'}"
                )

                system_instruction += "\nUse only these draft catalog IDs for hypotheses; clues are not diagnostic criteria:\n" + catalog_prompt()
                user_prompt = f"""Patient Opening Presentation:
- Body Site: {intake.body_site or 'Unspecified'}
- Reported Description: {intake.lesion_type or 'Skin issue'}
- Duration: {intake.duration_days or 'Unspecified'} days
- Itching: {'Yes' if intake.has_itching else 'No / Unspecified'}

Known patient-reported facts: {json.dumps({k: getattr(intake, k) for k in IntakeFacts.model_fields if getattr(intake, k) is not None}, ensure_ascii=False)}
Use these answers together with visible observations. Ask one relevant follow-up about something still unknown.
Examine the skin photo and return JSON ONLY with this schema:
{{
  "visual_morphology": "Description of morphological features observed in the image",
  "primary_hypothesis": "Leading suspected condition name (e.g. acanthosis_nigricans, scabies, psoriasis, etc.)",
  "candidate_differentials": ["Candidate 1", "Candidate 2", "Candidate 3", "Candidate 4"],
  "agent_question": "Spoken response to patient acknowledging visual findings and asking the first condition-specific discriminating question",
  "initial_confidence": 0.5 to 0.95
}}"""

                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": f"{system_instruction}\n\n{user_prompt}"},
                            {"inlineData": {"mimeType": "image/jpeg", "data": img_b64}}
                        ]
                    }],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "temperature": 0.1
                    }
                }

                resp = post_gemini(url, {"x-goog-api-key": self.gemini_key}, payload)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    parsed = json.loads(raw_text)
                    agent_q = sanitize_safety_constraints(parsed.get("agent_question", ""))
                    return {
                        "visual_morphology": parsed.get("visual_morphology", "Clinical skin examination"),
                        "primary_hypothesis": normalize_condition(parsed.get("primary_hypothesis")),
                        "candidate_differentials": list(dict.fromkeys(normalize_condition(c) for c in parsed.get("candidate_differentials", []))),
                        "agent_question": agent_q,
                        "initial_confidence": float(parsed.get("initial_confidence", 0.0)),
                        "vision_available": True
                    }
                raise ProviderError(f"Gemini photo analysis failed (HTTP {resp.status_code}).")
            except requests.Timeout as exc:
                raise ProviderError("Gemini photo analysis timed out after retries.") from exc
            except requests.RequestException as exc:
                raise ProviderError("The connection to Gemini photo analysis failed.") from exc
            except (ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
                raise ProviderError("Gemini returned an unusable photo analysis.") from exc

        # No image inference was completed. Continue collecting history without
        # inventing morphology or anchoring on a site-based disease label.
        return {
            "visual_morphology": None,
            "primary_hypothesis": "other_unclear",
            "candidate_differentials": [],
            "agent_question": (
                "फोटो मिल गई है, लेकिन अभी उसका विश्लेषण नहीं हो पाया। आपके बताए लक्षणों की जानकारी जारी रखते हैं।"
                if is_hi else
                "Your photo was received, but image analysis is temporarily unavailable. We can continue collecting your symptoms."
            ),
            "initial_confidence": 0.0,
            "vision_available": False,
        }

    def diagnose(
        self,
        image_bytes: bytes,
        intake: ClinicalIntakeSlots,
        classifier_pred: Optional[ImagePrediction] = None,
        language: str = "en"
    ) -> ClinicalReasonerOutput:
        """
        Performs direct multimodal image examination + intake analysis + web grounding.
        """
        is_hi = ("hi" in language.lower()) if language else ("hi" in (intake.primary_language or "").lower())

        # If API key is available, run multimodal visual diagnosis
        if self.gemini_key:
            try:
                return self._run_multimodal_vision_inference(
                    image_bytes=image_bytes,
                    intake=intake,
                    classifier_pred=classifier_pred,
                    language=language
                )
            except Exception as e:
                print(f"[MultimodalDermatologistAgent] Multimodal API error: {e}. Model unavailable.")

        # Model is unavailable (no API key or network error)
        # Avoid fallback heuristics to prevent unreliable or inaccurate clinical output
        unavailable_msg = (
            "एआई डायग्नोस्टिक मॉडल वर्तमान में उपलब्ध नहीं है। कृपया त्वचा की प्रत्यक्ष जांच हेतु किसी योग्य डॉक्टर से संपर्क करें।"
            if is_hi else
            "The AI diagnostic model is currently unavailable. Please consult a qualified clinician or dermatologist for an in-person physical examination."
        )
        return ClinicalReasonerOutput(
            assessment_source="unavailable",
            differential=[],
            top_diagnosis="other_unclear",
            final_confidence=0.0,
            identified_red_flags=[],
            synthesized_explanation=unavailable_msg,
            baseline_image_top=classifier_pred.top_condition if classifier_pred else "other_unclear",
            baseline_image_confidence=classifier_pred.confidence if classifier_pred else 0.0,
            gain_from_voice_history="Model currently unavailable"
        )

    def _run_multimodal_vision_inference(
        self,
        image_bytes: bytes,
        intake: ClinicalIntakeSlots,
        classifier_pred: Optional[ImagePrediction],
        language: str = "en"
    ) -> ClinicalReasonerOutput:
        # Encode image to base64
        pil_img = Image.open(io.BytesIO(image_bytes))
        # Ensure RGB
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        
        # Optimize size for transmission (max 1024x1024 while preserving fine morphology)
        pil_img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG", quality=90)
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        is_hi = ("hi" in language.lower()) if language else ("hi" in (intake.primary_language or "").lower())

        # Format clinical intake summary for prompt
        intake_summary = (
            f"- Body Site: {intake.body_site or 'Unspecified'}\n"
            f"- Reported Description: {intake.lesion_type or 'Rash/lesion'}\n"
            f"- Duration: {intake.duration_days} days\n"
            f"- Itching: {'Unknown' if intake.has_itching is None else ('Yes (pruritic)' if intake.has_itching else 'No')}\n"
            f"- Household Contacts Affected: {'Yes (contagious cluster)' if intake.household_contacts_affected else 'No / Unreported'}\n"
            f"- Fever: {'Unknown' if intake.has_fever is None else ('Yes (systemic signs)' if intake.has_fever else 'No')}\n"
            f"- Pain: {'Unknown' if intake.has_pain is None else ('Yes' if intake.has_pain else 'No')}\n"
            f"- Spreading: {'Unknown' if intake.is_spreading is None else ('Yes' if intake.is_spreading else 'No')}"
        )

        classifier_context = ""
        if classifier_pred:
            top_probs = sorted(classifier_pred.probabilities.items(), key=lambda x: x[1], reverse=True)[:3]
            prob_str = ", ".join([f"{k.value if hasattr(k, 'value') else k}: {v:.1%}" for k, v in top_probs])
            classifier_context = f"\nSecondary Reference Classifier Priors: {prob_str}"

        # Web search assistance if intake indicates specific complex presentation
        search_snippets = ""
        search_query = f"{intake.body_site or 'skin'} {intake.lesion_type or ''} dermatology treatment guidelines".strip()
        try:
            web_results = self.search_tool.search_clinical_guidelines(search_query, max_results=2)
            if web_results:
                search_snippets = "\nClinical Guidelines & Reference Web Search Results:\n" + "\n".join(
                    [f"- [{r['title']}]: {r['snippet']}" for r in web_results if r.get("snippet")]
                )
        except Exception:
            pass

        system_instruction = (
            "You are a Senior Consultant Multimodal Dermatologist examining an actual patient skin photograph.\n"
            "Examine the photograph directly with clinical visual acumen (evaluating lesion morphology, arrangement, "
            "margins, erythema, scaling, follicular plugging, burrows, or atypical pigmentation).\n"
            "Synthesize what you observe in the image with the patient's reported symptoms and the web search guidelines.\n\n"
            "CRITICAL DIAGNOSTIC GUIDELINES:\n"
            "1. Return provisional hypotheses only, using the supplied catalog IDs. Use other_unclear when evidence is insufficient.\n"
            "2. Identify when examination or clinician treatment is needed. Do not invent medication or treatment instructions.\n"
            "3. Red flags: suspected malignancy (asymmetry, irregular border, multiple colors), infant < 1 year, "
            "fever with rapidly spreading rash, or anaphylaxis/angioedema signs.\n"
            "4. If visual features in the photo are non-specific, subtle, or indeterminate, synthesize and weigh the patient's reported clinical history (e.g. nocturnal itching with household members affected on hands/wrists is classic Scabies transmission triad).\n"
            "5. Output valid JSON ONLY matching the required schema."
        )

        system_instruction += "\nDraft recognition catalog (not validated diagnostic criteria):\n" + catalog_prompt()
        user_prompt = f"""Patient Clinical History:
{intake_summary}
Additional patient-reported condition history (unverified):
{json.dumps(intake.condition_specific_history, ensure_ascii=False)}
{classifier_context}
{search_snippets}

Examine the attached skin photograph and return JSON ONLY with this schema:
{{
  "visual_findings": "Detailed description of morphological features observed in the image (borders, color, elevation, scaling)",
  "primary_diagnosis": "one exact condition_id from the supplied catalog, or other_unclear",
  "confidence": 0.0 to 1.0,
  "differential": [
    {{"condition": "Condition name", "probability": 0.0 to 1.0, "clinical_rationale": "Direct visual and symptom correlation"}}
  ],
  "identified_red_flags": []
}}"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        payload = {
            "contents": [{
                "parts": [
                    {"text": f"{system_instruction}\n\n{user_prompt}"},
                    {"inlineData": {"mimeType": "image/jpeg", "data": img_b64}}
                ]
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1
            }
        }

        resp = post_gemini(url, {"x-goog-api-key": self.gemini_key}, payload)
        if resp.status_code != 200:
            raise ProviderError(f"Gemini assessment failed (HTTP {resp.status_code}).")

        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        parsed = json.loads(raw_text)

        # Canonical IDs prevent free-text diagnoses bypassing catalog boundaries.
        top_cond = normalize_condition(parsed.get("primary_diagnosis", "other_unclear"))
        diff_items = [DifferentialDiagnosisItem(
            condition=normalize_condition(d.get("condition", "other_unclear")),
            probability=max(0.0, min(1.0, float(d.get("probability", 0.0)))),
            clinical_justification=d.get("clinical_rationale", "")
        ) for d in parsed.get("differential", [])]
        diff_items.sort(key=lambda item: item.probability, reverse=True)

        # Treatment comes from the catalog, not model-generated prescribing prose.
        # This is a clinician-facing draft; the policy service controls patient output.
        coverage = get_coverage(top_cond)
        sanitized_explanation = sanitize_safety_constraints(
            f"Provisional possibility: {coverage['display_name']}. "
            f"Basic care: {' '.join(coverage['basic_care']) or 'No condition-specific self-care pathway.'} "
            f"Clinician treatment overview: {coverage['treatment_summary']}"
        )

        baseline_top = classifier_pred.top_condition if classifier_pred else top_cond
        baseline_conf = classifier_pred.confidence if classifier_pred else max(0.0, min(1.0, float(parsed.get("confidence", 0.0))))
        final_conf = max(0.0, min(1.0, float(parsed.get("confidence", 0.0))))

        gain_summary = (
            f"Multimodal Visual Vision inspected image directly with +{round((final_conf - baseline_conf)*100, 1)}% confidence gain"
            if final_conf > baseline_conf else
            f"Multimodal Visual Vision confirmed {top_cond} as a provisional photographic hypothesis"
        )

        return ClinicalReasonerOutput(
            assessment_source="multimodal",
            differential=diff_items,
            top_diagnosis=top_cond,
            final_confidence=round(final_conf, 3),
            identified_red_flags=parsed.get("identified_red_flags", []),
            synthesized_explanation=sanitized_explanation,
            baseline_image_top=baseline_top,
            baseline_image_confidence=baseline_conf,
            gain_from_voice_history=gain_summary
        )
