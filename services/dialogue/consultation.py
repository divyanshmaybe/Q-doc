"""Explicit consultation actions; the language model cannot bypass readiness or safety."""
import json
import re

from services.policy.rules import sanitize_safety_constraints

FACTS = (
    "body_site", "lesion_type", "duration_days", "age", "has_itching", "has_fever",
    "has_pain", "is_spreading", "household_contacts_affected", "breathing_difficulty",
    "mucosal_involvement", "is_pregnant", "patient_concern", "daily_impact",
    "prior_treatments", "treatment_barriers", "safety_screen_complete", "nocturnal_itch", "triggers",
)
QUESTIONS = {
    "lesion_type": ("What does the affected skin look like — for example, bumps, scaling, or a change in colour?", "प्रभावित त्वचा कैसी दिखती है — दाने, पपड़ी या रंग में बदलाव?"),
    "age": ("How old is the person with the skin problem?", "जिस व्यक्ति को त्वचा की परेशानी है उसकी उम्र क्या है?"),
    "breathing_difficulty": ("Are you having difficulty breathing?", "क्या आपको सांस लेने में तकलीफ है?"),
    "mucosal_involvement": ("Do you have sores in your mouth or eyes, or skin peeling?", "क्या मुंह या आंखों में घाव, या त्वचा उतरने की समस्या है?"),
    "is_pregnant": ("Are you currently pregnant?", "क्या आप अभी गर्भवती हैं?"),
    "treatment_barriers": ("What would make the next step difficult for you?", "अगला कदम पूरा करने में क्या परेशानी होगी?"),
    "nocturnal_itch": ("Does the itching become worse at night?", "क्या खुजली रात में बढ़ती है?"),
    "triggers": ("Have you noticed a product, activity, or exposure that makes it worse?", "क्या किसी उत्पाद, काम या संपर्क से यह बढ़ता है?"),
    "body_site": ("Where on your body is the skin problem?", "यह परेशानी शरीर के किस हिस्से में है?"),
    "duration_days": ("When did this first begin?", "यह परेशानी कब शुरू हुई?"),
    "has_fever": ("Have you had a fever with this skin problem?", "क्या इस परेशानी के साथ बुखार भी है?"),
    "has_itching": ("Does the area itch?", "क्या इस हिस्से में खुजली होती है?"),
    "has_pain": ("Is the affected area painful?", "क्या इस हिस्से में दर्द है?"),
    "is_spreading": ("Is it spreading or changing quickly?", "क्या यह तेजी से फैल रहा है या बदल रहा है?"),
    "household_contacts_affected": ("Has anyone else at home developed similar itching? This helps distinguish some causes.", "क्या घर में किसी और को ऐसी खुजली है? इससे कुछ कारणों में अंतर समझने में मदद मिलती है।"),
    "prior_treatments": ("What have you tried on it, including creams or home remedies?", "आपने इसके लिए कौन सी क्रीम या घरेलू उपाय इस्तेमाल किए हैं?"),
    "patient_concern": ("What worries you most about this skin problem?", "इस परेशानी के बारे में आपको सबसे ज्यादा किस बात की चिंता है?"),
    "daily_impact": ("How is this affecting your sleep or daily activities?", "इससे आपकी नींद या रोजमर्रा के काम पर क्या असर पड़ रहा है?"),
    "safety_screen_complete": ("Before we continue, have you had trouble breathing, sores in your mouth or eyes, or skin peeling?", "आगे बढ़ने से पहले: क्या सांस लेने में तकलीफ, मुंह या आंखों में घाव, या त्वचा उतरने की समस्या है?"),
}


def intake_red_flags(slots):
    flags = []
    for field, flag in (("breathing_difficulty", "breathing_difficulty"),
                        ("mucosal_involvement", "mucosal_involvement"),
                        ("has_fever", "fever_with_rash"), ("is_pregnant", "pregnancy")):
        if getattr(slots, field, None) is True:
            flags.append(flag)
    if slots.age is not None and slots.age < 1:
        flags.append("infant_under_1_year")
    return flags


class ConsultationPlanner:
    def __init__(self, llm, max_turns=None):
        self.llm = llm
        self.max_turns = max_turns

    def step(self, slots, intent, history, lang):
        hi = lang.startswith("hi")
        choose = lambda en, hindi: hindi if hi else en
        raw = intent.get("raw_transcript", intent.get("clean_meaning", ""))
        lower = raw.lower().strip(" .!।")
        if slots.last_question_field and slots.last_question_field.startswith("condition_history:") and raw.strip():
            condition_id = slots.last_question_field.split(":", 1)[1]
            slots.condition_specific_history[condition_id] = {
                "patient_response": raw, "source": "patient", "clinically_verified": False,
            }
            slots.summary_confirmed = False
            slots.last_question_field = None
        for field in FACTS:
            slots.fact_status.setdefault(field, "not_asked" if getattr(slots, field) is None else "reported")
        slots.turn_count += 1
        slots.is_ready_for_photo = False
        slots.is_final_verdict_ready = False
        slots.is_complete = False
        # Recover snapshots created by the former missing=ambiguous bug. A batch
        # spanning most intake fields came from one answer, not individual uncertainties.
        if len(slots.pending_clarifications) >= 8:
            slots.pending_clarifications = []
        ambiguous = intent.get("ambiguous_fields", [])
        if not isinstance(ambiguous, list) or len(ambiguous) > 3:
            ambiguous = []
        for field in ambiguous:
            if field in FACTS and field not in slots.pending_clarifications:
                slots.pending_clarifications.append(field)
        for field in FACTS:
            value = intent.get(field)
            if field in ambiguous or value is None:
                continue
            old = getattr(slots, field)
            # Validate candidate fields through Pydantic before accepting LLM output.
            try:
                candidate = slots.model_copy().model_dump()
                candidate[field] = value
                value = type(slots).model_validate(candidate).__getattribute__(field)
            except (ValueError, TypeError):
                continue
            if field in ("age", "duration_days") and (value < 0 or (field == "age" and value > 120)):
                if field not in slots.pending_clarifications:
                    slots.pending_clarifications.append(field)
                continue
            if old != value:
                slots.fact_history.append({"field": field, "previous": old, "value": value,
                                           "source": "patient", "transcript": raw, "turn": slots.turn_count})
                setattr(slots, field, value)
                slots.summary_confirmed = False
                if field not in ("treatment_barriers", "patient_concern", "daily_impact"):
                    slots.reviewed_plan = None
            slots.fact_status[field] = "denied" if value is False else "reported"
            if field in slots.pending_clarifications:
                slots.pending_clarifications.remove(field)
        if slots.last_question_field == "safety_screen_complete":
            if lower in (
                "no", "none", "none of these", "no to all", "नहीं", "nahi", "नहीं इनमें से कुछ नहीं",
                "nothing like that", "neither", "neither of those", "none of them", "nothing"
            ) or any(term in lower for term in (
                "no trouble breathing", "no breathing difficulty", "there was no trouble breathing",
                "no mouth sores", "no eye sores", "no skin peeling", "nothing like that", "no sores",
                "no issues with breathing"
            )):
                slots.safety_screen_complete = True
        if any(word in lower for word in ("not achieved", "notes on teaching")):
            if "has_itching" not in slots.pending_clarifications:
                slots.pending_clarifications.append("has_itching")
        if any(word in lower for word in ("no photo", "cannot take a photo", "skip photo", "फोटो नहीं")):
            slots.photo_declined = True
        if slots.consultation_stage == "summary" and lower in (
            "yes", "correct", "that's right", "that is right", "yes correct", "हाँ", "हां", "haan", "sahi hai"
        ):
            slots.summary_confirmed = True

        def respond(action, stage, message, field=None):
            slots.planned_action = action
            slots.consultation_stage = stage
            slots.last_question_field = field
            if field and not field.startswith("condition_history:") and getattr(slots, field, None) is None:
                slots.fact_status[field] = "uncertain" if action == "clarify" else "asked_unknown"
            slots.is_ready_for_photo = action == "request_photo"
            slots.is_final_verdict_ready = action == "explain_assessment"
            slots.is_complete = slots.is_final_verdict_ready or action == "handoff"
            return slots, message, slots.is_ready_for_photo, None

        flags = intake_red_flags(slots)
        if flags:
            slots.handoff_required = True
            slots.handoff_urgency = "emergency" if "breathing_difficulty" in flags else "seek_opd"
            message = choose(
                "Trouble breathing needs emergency help now. Please seek emergency care rather than continuing this screening."
                if "breathing_difficulty" in flags else
                "Your symptoms or circumstances need direct clinical assessment. Please arrange prompt in-person care; this screening cannot safely provide a treatment plan.",
                "सांस लेने में तकलीफ के लिए अभी आपातकालीन सहायता लें।" if "breathing_difficulty" in flags else
                "आपके लक्षण या परिस्थिति में डॉक्टर की सीधी जांच जरूरी है। कृपया जल्द प्रत्यक्ष जांच करवाएं।")
            return respond("handoff", "handoff", message)
        if slots.handoff_required:
            return respond("handoff", "handoff", choose("Please follow the referral advice. I can help clarify the next step, but cannot replace the examination.", "कृपया डॉक्टर से जांच की सलाह का पालन करें। मैं अगला कदम समझाने में मदद कर सकता हूं।"))
        if slots.pending_clarifications:
            field = slots.pending_clarifications[0]
            question = QUESTIONS.get(field, ("Could you clarify that detail?", "कृपया यह जानकारी स्पष्ट करें।"))[hi]
            return respond("clarify", "history", choose("I am not certain I heard that correctly. ", "मुझे यह बात साफ समझ नहीं आई। ") + question, field)
        if slots.reviewed_plan:
            if any(w in lower for w in ("afford", "cost", "expensive", "पैसे", "महंगा")):
                slots.treatment_barriers = raw
                return respond("discuss_barriers", "follow_up", choose(
                    "Cost is an important concern. You can ask a nearby public clinic about available services and charges. Which part of the next step would be hardest to arrange?",
                    "खर्च की चिंता महत्वपूर्ण है। नजदीकी सरकारी क्लिनिक में उपलब्ध सेवाओं और शुल्क की जानकारी ले सकते हैं। अगला कदम पूरा करने में सबसे बड़ी परेशानी क्या है?"))
            if any(w in lower for w in ("worse", "burning", "made it worse", "बिगड़", "जलन")):
                slots.handoff_required = True
                slots.handoff_urgency = "seek_opd"
                return respond("handoff", "handoff", choose(
                    "New or worsening symptoms need a clinician review. Which symptom has changed? Seek urgent help for breathing difficulty, mouth or eye sores, or rapidly worsening illness.",
                    "नए या बिगड़ते लक्षणों के लिए डॉक्टर की जांच जरूरी है। कौन सा लक्षण बदला है? सांस की तकलीफ, मुंह या आंख में घाव, या तेजी से हालत बिगड़ने पर तुरंत सहायता लें।"))
            return respond("check_understanding", "follow_up", choose(
                "Your recorded next step is: " + slots.reviewed_plan + " What questions or practical difficulties do you have with that next step?",
                "आपका दर्ज अगला कदम है: " + slots.reviewed_plan + " इसे करने में कोई सवाल या परेशानी है?"))
        required = ["body_site", "duration_days", "has_fever", "safety_screen_complete", "has_itching", "has_pain", "is_spreading", "prior_treatments"]
        if slots.has_itching:
            required.extend(["household_contacts_affected", "nocturnal_itch"])
        if any(term in " ".join(slots.suspected_differentials).lower() for term in ("eczema", "dermatitis", "urticaria")):
            required.append("triggers")
        required.extend(["patient_concern", "daily_impact"])
        missing = [field for field in required if getattr(slots, field) is None]
        slots.missing_required_slots = missing
        if self.max_turns is not None and slots.turn_count >= self.max_turns and missing:
            slots.handoff_required = True
            slots.handoff_urgency = "seek_opd"
            return respond("handoff", "handoff", choose("We still have important unanswered questions. Please have a clinician complete the assessment.", "कुछ जरूरी जानकारी अभी बाकी है। कृपया डॉक्टर से जांच पूरी करवाएं।"))
        if missing:
            field = missing[0]
            fallback = QUESTIONS[field][hi]
            if field == "has_pain" and re.search(r"\b(itch\w*)\b|खुजली|khujli", lower):
                fallback = choose(
                    "I've noted the itching. Is there pain as well, or only itching?",
                    "खुजली की बात दर्ज है। क्या साथ में दर्द भी है, या केवल खुजली है?"
                )
            # Acknowledge the patient's words without allowing generated clinical advice.
            if slots.turn_count == 1 and slots.body_site:
                fallback = choose(
                    f"I've noted {slots.lesion_type or 'the skin problem'} on your {slots.body_site}. ",
                    f"आपके {slots.body_site} की परेशानी दर्ज कर ली है। "
                ) + fallback
            return respond("ask_question", "history", fallback, field)
        if not slots.photo_image_id and not slots.photo_declined:
            return respond("request_photo", "photo", choose(
                "If you are comfortable, take a clear photo in good light. Avoid including your face or identifying details unless needed; for a private area, you may skip the photo and arrange an examination.",
                "यदि आप सहज हों तो अच्छी रोशनी में साफ फोटो लें। जरूरी न हो तो पहचान दिखाने से बचें। निजी हिस्से की फोटो छोड़कर डॉक्टर से जांच करवा सकते हैं।"))
        if slots.photo_image_id:
            from services.clinical_knowledge.coverage import get_coverage
            coverage = get_coverage(slots.primary_suspected_condition)
            condition_id = coverage["condition_id"]
            if condition_id != "other_unclear" and condition_id not in slots.condition_specific_history:
                # Capture the answer verbatim; do not manufacture structured diagnostic findings.
                from services.clinical_knowledge.questions import screening_question
                prompt = screening_question(condition_id, lang)
                return respond("ask_question", "history", prompt, f"condition_history:{condition_id}")
        if not slots.summary_confirmed:
            summary = choose(
                f"Let me check: {slots.lesion_type or 'a skin problem'} on your {slots.body_site}, starting about {slots.duration_days} days ago. Your main concern is: {slots.patient_concern}. Is that correct, or should I change anything?",
                f"मैं पुष्टि कर लूं: {slots.body_site} पर {slots.lesion_type or 'त्वचा की परेशानी'} लगभग {slots.duration_days} दिन से है। आपकी मुख्य चिंता: {slots.patient_concern}। क्या यह सही है, या कुछ बदलना है?")
            return respond("summarize", "summary", summary)
        if slots.photo_declined:
            slots.handoff_required = True
            slots.handoff_urgency = "seek_opd"
            return respond("handoff", "handoff", choose("I have recorded your history. An in-person examination is the next step because we do not have a photograph to assess.", "आपकी जानकारी दर्ज है। फोटो के बिना अगला कदम डॉक्टर द्वारा प्रत्यक्ष जांच है।"))
        return respond("explain_assessment", "assessment", choose(
            "Thank you for confirming. I will prepare a provisional assessment and check which next steps are appropriate. A photograph cannot confirm a diagnosis.",
            "पुष्टि के लिए धन्यवाद। अब मैं प्रारंभिक आकलन और उचित अगला कदम तैयार करूंगा। केवल फोटो से निदान की पुष्टि नहीं होती।"))
