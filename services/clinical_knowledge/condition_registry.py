"""
Expanded 24-Condition Clinical Registry for Q-Doc Track B.
Specifies required evidence (history, visual, lab/test), mandatory confirmatory test
that settles the diagnosis, ICD-10 mapping, urgency level, and provisional language constraints.
Adheres strictly to IADVL and AAD primary care dermatology guidelines.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ClinicalUrgency(str, Enum):
    ROUTINE = "routine"
    SEEK_OPD = "seek_opd"
    EMERGENCY = "emergency"


class ConditionSpec(BaseModel):
    condition_id: str
    display_name: str
    hindi_name: str
    icd10: str
    urgency: ClinicalUrgency
    category: str
    is_dangerous_red_flag: bool = False
    
    # Clinical Evidence Requirements
    required_history_evidence: List[str]
    required_visual_morphology: List[str]
    predilection_sites: List[str]
    
    # Definitive Confirmatory Test (Cannot be diagnosed definitively without this)
    confirmatory_test_required: str
    confirmatory_test_description: str
    
    # What cannot be confirmed without the test
    diagnostic_limitation: str
    
    # Provisional Patient Guidance (Bilingual)
    provisional_summary_en: str
    provisional_summary_hi: str


EXPANDED_24_CONDITIONS: Dict[str, ConditionSpec] = {
    # ── 1. Acne Vulgaris ──
    "acne_vulgaris": ConditionSpec(
        condition_id="acne_vulgaris",
        display_name="Acne Vulgaris",
        hindi_name="मुँहासे (Acne Vulgaris)",
        icd10="L70.0",
        urgency=ClinicalUrgency.ROUTINE,
        category="appendageal",
        required_history_evidence=["adolescent or young adult onset", "gradual onset over weeks to months", "fluctuates with stress/cosmetics"],
        required_visual_morphology=["open comedones (blackheads)", "closed comedones (whiteheads)", "inflammatory papules and pustules"],
        predilection_sites=["face (cheeks, forehead, chin)", "upper chest", "upper back", "shoulders"],
        confirmatory_test_required="Clinical Dermoscopy / Comedone Extraction",
        confirmatory_test_description="Dermatoscopic identification of follicular keratotic plugs and polar comedones distinguishes from acneiform folliculitis.",
        diagnostic_limitation="Differentiating true acne vulgaris from steroid-induced acneiform eruption or Demodex folliculitis requires medication review and dermoscopy.",
        provisional_summary_en="Provisional finding: Acne Vulgaris pattern. Recommended confirmatory assessment: in-person clinical evaluation to classify comedonal vs inflammatory subtype before initiating treatment.",
        provisional_summary_hi="अनंतिम निष्कर्ष: मुँहासे (Acne) के लक्षण। उपचार शुरू करने से पहले क्लिनिकल जांच की सलाह दी जाती है।"
    ),

    # ── 2. Eczema / Atopic Dermatitis ──
    "eczema": ConditionSpec(
        condition_id="eczema",
        display_name="Eczema (Atopic Dermatitis)",
        hindi_name="एक्जिमा (Atopic Dermatitis)",
        icd10="L20",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="inflammatory",
        required_history_evidence=["pruritus (itch)", "chronicity (>4 weeks or recurring)", "personal/family history of atopy (asthma/allergic rhinitis)"],
        required_visual_morphology=["erythematous ill-defined patches", "xerosis (dry skin)", "excoriations", "lichenification in chronic phase"],
        predilection_sites=["antecubital fossae (inner elbows)", "popliteal fossae (behind knees)", "flexor wrists", "neck", "eyelids"],
        confirmatory_test_required="Patch Testing / Serum Total IgE",
        confirmatory_test_description="Standardized European/Indian Patch Testing series to rule out superimposed allergic contact dermatitis.",
        diagnostic_limitation="Cannot distinguish pure intrinsic atopic dermatitis from secondary allergic contact dermatitis without patch testing.",
        provisional_summary_en="Provisional finding: Eczematous Dermatitis pattern. Recommended confirmatory test: Patch testing if contact allergen suspected, alongside in-person clinical staging.",
        provisional_summary_hi="अनंतिम निष्कर्ष: एक्जिमा (त्वचा की सूजन) के लक्षण। एलर्जी के सटीक कारण का पता लगाने के लिए पैच टेस्ट की सलाह दी जाती है।"
    ),

    # ── 3. Psoriasis Vulgaris ──
    "psoriasis": ConditionSpec(
        condition_id="psoriasis",
        display_name="Psoriasis Vulgaris",
        hindi_name="सोरायसिस (Psoriasis Vulgaris)",
        icd10="L40.0",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="papulosquamous",
        required_history_evidence=["chronic recurrent plaques (>1-2 months)", "worsening in winter", "family history of psoriasis"],
        required_visual_morphology=["sharply demarcated erythematous plaques", "silvery-white micaceous scales", "Auspitz sign"],
        predilection_sites=["extensor surfaces (knees, elbows)", "scalp", "lumbosacral region", "umbilicus", "nails"],
        confirmatory_test_required="Skin Punch Biopsy (Histopathology)",
        confirmatory_test_description="4mm punch biopsy demonstrating regular epidermal hyperplasia, Munro microabscesses, and hypogranulosis.",
        diagnostic_limitation="Atypical plaque psoriasis vs psoriasiform tinea or lichen simplex chronicus cannot be definitively confirmed without histopathology or KOH mount.",
        provisional_summary_en="Provisional finding: Plaque Psoriasis pattern. Recommended confirmatory test: Dermatoscopy and skin punch biopsy if atypical, before systemic therapy.",
        provisional_summary_hi="अनंतिम निष्कर्ष: सोरायसिस के लक्षण। सटीक पुष्टि के लिए त्वचा रोग विशेषज्ञ द्वारा बायोप्सी की आवश्यकता हो सकती है।"
    ),

    # ── 4. Tinea Corporis / Cruris (Ringworm) ──
    "tinea": ConditionSpec(
        condition_id="tinea",
        display_name="Tinea (Dermatophytosis / Ringworm)",
        hindi_name="दाद / फंगल संक्रमण (Tinea)",
        icd10="B35",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="infectious_fungal",
        required_history_evidence=["progressive centrifugal spread", "pruritus aggravated by sweat/heat", "prior use of topical steroid creams"],
        required_visual_morphology=["annular plaque with raised erythematous scaly border", "central clearing", "occasional peripheral pustules"],
        predilection_sites=["groin / inner thighs (cruris)", "trunk / abdomen (corporis)", "feet / web spaces (pedis)", "face (faciei)"],
        confirmatory_test_required="Potassium Hydroxide (KOH) Mount / Fungal Culture",
        confirmatory_test_description="Microscopic 10-20% KOH examination of peripheral scale scrapings revealing branching septate hyphae.",
        diagnostic_limitation="Tinea incognito (steroid-altered ringworm) mimics eczema and cannot be safely diagnosed without microscopic KOH hyphae confirmation.",
        provisional_summary_en="Provisional finding: Superficial Tinea (Fungal Ringworm) pattern. Mandatory confirmatory test: Skin scraping with KOH mount before starting antifungal regimens.",
        provisional_summary_hi="अनंतिम निष्कर्ष: दाद (फंगल संक्रमण) की संभावना। उपचार से पहले त्वचा की खुरचन का KOH टेस्ट करवाना अनिवार्य है।"
    ),

    # ── 5. Urticaria ──
    "urticaria": ConditionSpec(
        condition_id="urticaria",
        display_name="Urticaria (Hives / Wheals)",
        hindi_name="पित्ती (Urticaria / Hives)",
        icd10="L50",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="allergic_reactive",
        required_history_evidence=["evanescent lesions resolving within 24 hours", "intense itching or burning", "possible drug/food/infection trigger"],
        required_visual_morphology=["edematous erythematous wheals with pale centers", "blanching on pressure", "geographic migratory shapes"],
        predilection_sites=["widespread across trunk", "extremities", "face"],
        confirmatory_test_required="Complete Blood Count (CBC) & Autologous Serum Skin Test (ASST)",
        confirmatory_test_description="CBC with differential (eosinophil count) and ASST for chronic autoimmune urticaria evaluation.",
        diagnostic_limitation="Urticarial vasculitis (lesions persisting >24h with residual purpura) requires a skin biopsy to distinguish from benign urticaria.",
        provisional_summary_en="Provisional finding: Acute/Subacute Urticaria pattern. Recommended confirmatory test: Clinical monitoring of wheal resolution (<24h) and allergy workup if recurrent.",
        provisional_summary_hi="अनंतिम निष्कर्ष: पित्ती (Urticaria) के लक्षण। यदि चकत्ते 24 घंटे से अधिक टिकते हैं या सांस लेने में तकलीफ हो तो तत्काल डॉक्टर से मिलें।"
    ),

    # ── 6. Scabies Infestation ──
    "scabies": ConditionSpec(
        condition_id="scabies",
        display_name="Scabies Infestation",
        hindi_name="स्केबीज (खाज / Scabies)",
        icd10="B86",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="infectious_parasitic",
        required_history_evidence=["severe nocturnal pruritus", "household or close contacts simultaneously affected", "symptoms >2 weeks"],
        required_visual_morphology=["intraepidermal linear burrows", "excoriated inflammatory papules", "pruritic genital or axillary nodules"],
        predilection_sites=["interdigital finger web-spaces", "flexor wrists", "anterior axillary folds", "umbilicus", "genitalia / scrotum"],
        confirmatory_test_required="Microscopic Mineral Oil Scraping / Dermoscopic Delta-Wing Sign",
        confirmatory_test_description="Direct skin scraping of burrow under light microscopy demonstrating Sarcoptes scabiei mite, ova, or scybala (feces).",
        diagnostic_limitation="Papular eczema and post-scabetic prurigo can clinically mimic active scabies; active infestation requires microscopic or high-resolution dermoscopic confirmation.",
        provisional_summary_en="Provisional finding: Scabies Infestation pattern. Mandatory confirmatory test: Burrow scraping or dermoscopy confirming mite presence before whole-family treatment.",
        provisional_summary_hi="अनंतिम निष्कर्ष: स्केबीज (खाज) के लक्षण। पूरे परिवार के उपचार से पहले डर्मोस्कोपी या माइक्रोस्कोपिक जांच द्वारा पुष्टि आवश्यक है।"
    ),

    # ── 7. Suspicious Melanoma / Neoplastic Lesion ──
    "possible_malignancy": ConditionSpec(
        condition_id="possible_malignancy",
        display_name="Suspicious Cutaneous Lesion (Possible Malignancy)",
        hindi_name="संदेहास्पद त्वचा गांठ / काला तिल",
        icd10="C43 / C44",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="neoplastic",
        is_dangerous_red_flag=True,
        required_history_evidence=["change in size, shape, or color of pre-existing mole", "bleeding or ulceration without trauma", "onset >40 years or acral site"],
        required_visual_morphology=["ABCDE criteria (Asymmetry, Border irregularity, Color variegation, Diameter >6mm, Evolution)", "ugly duckling sign"],
        predilection_sites=["palms and soles (acral lentiginous in Indian skin)", "under nails (subungual)", "face / neck / ears", "back"],
        confirmatory_test_required="Excisional Biopsy with Histopathology",
        confirmatory_test_description="Complete narrow-margin excisional biopsy with Breslow thickness micro-staging and immunohistochemistry (Melan-A, S100, HMB45).",
        diagnostic_limitation="Visual or AI algorithms can NEVER confirm or exclude skin cancer; definitive diagnosis is strictly histopathological.",
        provisional_summary_en="CRITICAL: Suspicious pigmented lesion requiring urgent formal in-person dermatologist evaluation. Mandatory confirmatory test: Excisional biopsy with histopathology.",
        provisional_summary_hi="अति महत्वपूर्ण: असामान्य तिल या गांठ। कैंसर के खतरे की जांच हेतु तत्काल त्वचा रोग विशेषज्ञ से बायोप्सी करवाना अनिवार्य है।"
    ),

    # ── 8. Seborrheic Dermatitis ──
    "seborrheic_dermatitis": ConditionSpec(
        condition_id="seborrheic_dermatitis",
        display_name="Seborrheic Dermatitis",
        hindi_name="सेबोरिक डर्मेटाइटिस (रूसी / पपड़ीदार त्वचा)",
        icd10="L21",
        urgency=ClinicalUrgency.ROUTINE,
        category="inflammatory",
        required_history_evidence=["chronic flaking of scalp or facial folds", "waxes and wanes with stress and seasonal changes", "mild itch"],
        required_visual_morphology=["greasy yellowish scales over erythematous patches", "predilection for sebum-rich zones"],
        predilection_sites=["scalp (dandruff)", "eyebrows", "nasolabial folds", "glabella", "conchal bowls of ears", "mid-chest"],
        confirmatory_test_required="Clinical Dermatoscopy / KOH rule-out",
        confirmatory_test_description="Dermoscopy demonstrating dotted vessels and greasy yellow scaling; KOH scraping to exclude Tinea faciei.",
        diagnostic_limitation="Differentiating seborrheic dermatitis from lupus erythematosus (malar rash) or rosacea requires clinical laboratory correlation.",
        provisional_summary_en="Provisional finding: Seborrheic Dermatitis pattern. Recommended confirmatory test: Clinical dermoscopy and fungal rule-out.",
        provisional_summary_hi="अनंतिम निष्कर्ष: सेबोरिक डर्मेटाइटिस के लक्षण। चेहरे व सिर की त्वचा के लिए डॉक्टर से प्रत्यक्ष जांच करवाएं।"
    ),

    # ── 9. Lichen Planus ──
    "lichen_planus": ConditionSpec(
        condition_id="lichen_planus",
        display_name="Lichen Planus",
        hindi_name="लाइकेन प्लेनस (Lichen Planus)",
        icd10="L43",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="papulosquamous",
        required_history_evidence=["intense pruritus out of proportion to rash", "subacute onset over weeks", "possible oral/genital soreness"],
        required_visual_morphology=["6 Ps: Planar, Polygonal, Purple/Violaceous, Pruritic, Papules, Plaques", "Wickham striae (lacy white network)", "Koebner phenomenon"],
        predilection_sites=["flexor wrists", "lumbar back", "shins", "ankles", "oral buccal mucosa", "genitalia"],
        confirmatory_test_required="Skin Punch Biopsy (Histopathology)",
        confirmatory_test_description="Demonstrates band-like lymphocytic infiltrate at dermo-epidermal junction (lichenoid interface dermatitis) and Civatte bodies.",
        diagnostic_limitation="Cannot distinguish idiopathic lichen planus from lichenoid drug eruption without clinical drug history and biopsy.",
        provisional_summary_en="Provisional finding: Lichen Planus pattern. Recommended confirmatory test: Punch biopsy of violaceous papule and oral mucosa examination.",
        provisional_summary_hi="अनंतिम निष्कर्ष: लाइकेन प्लेनस के लक्षण। पुष्टि के लिए त्वचा बायोप्सी और मुंह की जांच आवश्यक है।"
    ),

    # ── 10. Vitiligo ──
    "vitiligo": ConditionSpec(
        condition_id="vitiligo",
        display_name="Vitiligo",
        hindi_name="विटिलिगो (सफेद दाग / Vitiligo)",
        icd10="L80",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="pigmentary",
        required_history_evidence=["asymptomatic depigmented white patches", "gradual progression", "often triggered at sites of friction/trauma"],
        required_visual_morphology=["chalky, milky-white macules with sharp borders", "absence of epidermal scale or atrophy", "trichrome or leukotrichia (white hair)"],
        predilection_sites=["periorificial (lips, eyelids)", "hands / fingertips (acrofacial)", "wrists", "extensor knees", "genitalia"],
        confirmatory_test_required="Wood's Lamp Examination / Thyroid Profile",
        confirmatory_test_description="Wood's light (365nm UV) produces brilliant blue-white fluorescence highlighting complete epidermal melanin loss.",
        diagnostic_limitation="Differentiating early vitiligo from post-inflammatory hypopigmentation, leprosy (Hansen's), or pityriasis versicolor requires Wood's lamp and sensory testing.",
        provisional_summary_en="Provisional finding: Vitiligo pattern. Mandatory confirmatory test: Wood's lamp examination and sensory evaluation to exclude Hansen's disease.",
        provisional_summary_hi="अनंतिम निष्कर्ष: विटिलिगो (सफेद दाग) की संभावना। वुड्स लैंप टेस्ट और संवेदी जांच द्वारा पुष्टि आवश्यक है।"
    ),

    # ── 11. Pityriasis Versicolor ──
    "pityriasis_versicolor": ConditionSpec(
        condition_id="pityriasis_versicolor",
        display_name="Pityriasis Versicolor (Tinea Versicolor)",
        hindi_name="पिटिरियासिस वर्सीकलर (सेहुआ / Tinea Versicolor)",
        icd10="B36.0",
        urgency=ClinicalUrgency.ROUTINE,
        category="infectious_fungal",
        required_history_evidence=["recurrence during hot/humid seasons", "mild or absent itch", "cosmetic distress due to discoloration"],
        required_visual_morphology=["hypopigmented or hyperpigmented scaly macules/patches", "fine furfuraceous scale on stretching (Coup d'ongle sign)"],
        predilection_sites=["upper trunk", "chest", "back", "neck", "upper arms"],
        confirmatory_test_required="10% KOH Examination (Spaghetti and Meatballs sign)",
        confirmatory_test_description="Demonstrates classic cluster of round yeast cells and short curved pseudohyphae of Malassezia globosa under microscopy.",
        diagnostic_limitation="Hypopigmented variant on darker skin tones mimics early vitiligo or progressive macular hypomelanosis.",
        provisional_summary_en="Provisional finding: Pityriasis Versicolor pattern. Recommended confirmatory test: KOH mount scraping demonstrating Malassezia elements.",
        provisional_summary_hi="अनंतिम निष्कर्ष: पिटिरियासिस वर्सीकलर (सेहुआ) के लक्षण। त्वचा खुरचन की माइक्रोस्कोपिक जांच से पुष्टि की जा सकती है।"
    ),

    # ── 12. Pityriasis Rosea ──
    "pityriasis_rosea": ConditionSpec(
        condition_id="pityriasis_rosea",
        display_name="Pityriasis Rosea",
        hindi_name="पिटिरियासिस रोजिया (Pityriasis Rosea)",
        icd10="L42",
        urgency=ClinicalUrgency.ROUTINE,
        category="papulosquamous",
        required_history_evidence=["preceding single primary patch (herald patch) 1-2 weeks prior", "subsequent eruptive shower across trunk", "mild itch"],
        required_visual_morphology=["herald patch (2-5cm oval salmon-colored plaque)", "secondary smaller oval plaques aligned along skin cleavage lines (Christmas tree pattern)", "inward-facing collarette of scale"],
        predilection_sites=["trunk", "abdomen", "neck", "proximal extremities"],
        confirmatory_test_required="VDRL / RPR Syphilis Serology & KOH",
        confirmatory_test_description="RPR/VDRL serology is mandatory to rule out Secondary Syphilis, which can present identically with collarette scaling.",
        diagnostic_limitation="Secondary Syphilis (the great imitator) and Guttate Psoriasis cannot be safely ruled out visually without serology.",
        provisional_summary_en="Provisional finding: Pityriasis Rosea pattern. Recommended confirmatory protocol: RPR serology to definitively exclude secondary syphilis mimicking this eruption.",
        provisional_summary_hi="अनंतिम निष्कर्ष: पिटिरियासिस रोजिया के लक्षण। सिफलिस जैसे अन्य संक्रमणों को बाहर करने के लिए ब्लड टेस्ट की सलाह दी जाती है।"
    ),

    # ── 13. Impetigo (Bacterial) ──
    "impetigo": ConditionSpec(
        condition_id="impetigo",
        display_name="Impetigo (Bacterial Pyoderma)",
        hindi_name="इम्पेटिगो (मवाददार दाने / Impetigo)",
        icd10="L01",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="infectious_bacterial",
        required_history_evidence=["rapidly spreading superficial sores in children/young adults", "oozing fluid that dries", "contagious clustering"],
        required_visual_morphology=["thin-walled fragile vesicles or pustules rupturing into characteristic honey-colored (meliceric) adherent crusts", "erythematous moist base"],
        predilection_sites=["perioral face", "around nostrils", "extremities", "hands"],
        confirmatory_test_required="Gram Stain & Bacterial Wound Culture with Sensitivity",
        confirmatory_test_description="Gram-positive cocci in clusters (Staphylococcus aureus) or chains (Streptococcus pyogenes); identifies MRSA resistance profiles.",
        diagnostic_limitation="Impetigo vs impetiginized eczema or herpes simplex requires bacterial swab culture.",
        provisional_summary_en="Provisional finding: Impetigo (Bacterial Infection) pattern. Recommended confirmatory test: Bacterial culture swab and antibiotic sensitivity profile.",
        provisional_summary_hi="अनंतिम निष्कर्ष: इम्पेटिगो (बैक्टीरियल संक्रमण) के लक्षण। मवाद की कल्चर जांच करवाकर उचित एंटीबायोटिक की सलाह लें।"
    ),

    # ── 14. Herpes Zoster (Shingles) ──
    "herpes_zoster": ConditionSpec(
        condition_id="herpes_zoster",
        display_name="Herpes Zoster (Shingles)",
        hindi_name="हरपीज जोस्टर (नागिन / Shingles)",
        icd10="B02",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="infectious_viral",
        is_dangerous_red_flag=False,
        required_history_evidence=["prodromal severe burning, tingling, or lancinating dermatomal pain preceding rash by 2-5 days", "strictly unilateral"],
        required_visual_morphology=["grouped umbilicated vesicles on an erythematous base strictly respecting the anatomical midline in a dermatomal distribution"],
        predilection_sites=["thoracic dermatomes (T3-T12)", "ophthalmic branch of trigeminal nerve (V1)", "cervical dermatomes"],
        confirmatory_test_required="Tzanck Smear / VZV Real-Time PCR",
        confirmatory_test_description="Tzanck cytology showing multinucleated giant cells and inclusion bodies; VZV PCR provides definitive molecular confirmation.",
        diagnostic_limitation="Herpes simplex zosteriform distribution vs Varicella Zoster virus requires PCR differentiation.",
        provisional_summary_en="Provisional finding: Herpes Zoster (Shingles) pattern. Urgent confirmatory protocol: In-person clinical exam (within 72 hours for antiviral efficacy) and ophthalmic consult if forehead/eye involved.",
        provisional_summary_hi="अनंतिम निष्कर्ष: हरपीज जोस्टर (नागिन) के लक्षण। 72 घंटे के भीतर डॉक्टर से मिलकर एंटीवायरल उपचार शुरू करवाना आवश्यक है।"
    ),

    # ── 15. Melasma ──
    "melasma": ConditionSpec(
        condition_id="melasma",
        display_name="Melasma (Chloasma)",
        hindi_name="मेलास्मा (झाइयां / Melasma)",
        icd10="L81.1",
        urgency=ClinicalUrgency.ROUTINE,
        category="pigmentary",
        required_history_evidence=["gradual onset of facial pigmentation", "exacerbation by sun exposure, pregnancy, or oral contraceptives", "predominantly females"],
        required_visual_morphology=["reticulated, symmetric, light-to-dark brown macules and patches with irregular geographic borders"],
        predilection_sites=["malar cheeks", "forehead", "upper cutaneous lip", "nasal bridge", "mandible (centrofacial or malar pattern)"],
        confirmatory_test_required="Wood's Lamp Examination / Cross-Polarized Dermoscopy",
        confirmatory_test_description="Classifies pigment depth into epidermal (accentuated under Wood's light), dermal (unaccentuated), or mixed.",
        diagnostic_limitation="Differentiating melasma from Riehl's melanosis, exogenous ochronosis, or lichen planus pigmentosus requires dermoscopy or histology.",
        provisional_summary_en="Provisional finding: Melasma pattern. Recommended confirmatory test: Wood's lamp examination and dermoscopic pigment depth staging before cosmetic interventions.",
        provisional_summary_hi="अनंतिम निष्कर्ष: मेलास्मा (झाइयां) के लक्षण। पिगमेंट की गहराई जांचने के लिए वुड्स लैंप जांच की सलाह दी जाती है।"
    ),

    # ── 16. Verruca Vulgaris (Viral Warts) ──
    "verruca_vulgaris": ConditionSpec(
        condition_id="verruca_vulgaris",
        display_name="Verruca Vulgaris (Common Viral Warts)",
        hindi_name="मस्सा (Verruca / Warts)",
        icd10="B07",
        urgency=ClinicalUrgency.ROUTINE,
        category="infectious_viral",
        required_history_evidence=["painless or pressure-tender firm growths persisting for months", "slow growth", "possible spread to adjacent sites"],
        required_visual_morphology=["hyperkeratotic, exophytic, rough verrucous papules/plaques", "black punctate dots on dermoscopy representing thrombosed dermal capillaries"],
        predilection_sites=["hands", "periungual (around nails)", "plantar soles (verruca plantaris)", "knees"],
        confirmatory_test_required="Dermatoscopy (Capillaries Visualization) / Pairing",
        confirmatory_test_description="Superficial scalpel paring of keratin reveals pinpoint bleeding from thrombosed papillary loops, distinguishing wart from corn/callus.",
        diagnostic_limitation="Plantar wart vs benign corn/callus or verrucous carcinoma requires paring and dermoscopic evaluation.",
        provisional_summary_en="Provisional finding: Verruca Vulgaris (Viral Wart) pattern. Recommended confirmatory test: In-person dermoscopy and paring assessment.",
        provisional_summary_hi="अनंतिम निष्कर्ष: सामान्य मस्सा (Wart) के लक्षण। कॉर्न्स से अलग पहचान के लिए डॉक्टर से प्रत्यक्ष जांच करवाएं।"
    ),

    # ── 17. Alopecia Areata ──
    "alopecia_areata": ConditionSpec(
        condition_id="alopecia_areata",
        display_name="Alopecia Areata",
        hindi_name="एलोपेसिया एरीटा (बाल झड़ना / Alopecia Areata)",
        icd10="L63",
        urgency=ClinicalUrgency.ROUTINE,
        category="hair_scalp",
        required_history_evidence=["sudden onset of discrete round bald patches over scalp or beard", "absence of redness or itching"],
        required_visual_morphology=["smooth circular patch of non-scarring hair loss", "exclamation mark hairs at periphery (narrower at base)", "yellow/black dots on dermoscopy"],
        predilection_sites=["scalp", "beard (alopecia barbae)", "eyebrows"],
        confirmatory_test_required="Trichoscopy (Scalp Dermoscopy) / Hair Pull Test",
        confirmatory_test_description="Trichoscopy revealing exclamation mark hairs, yellow dots, and cadaverized hairs; hair pull test active at margin.",
        diagnostic_limitation="Alopecia areata vs Tinea capitis, trichotillomania, or early cicatricial alopecia requires trichoscopy and fungal scrapings.",
        provisional_summary_en="Provisional finding: Alopecia Areata pattern. Recommended confirmatory test: Trichoscopy (digital hair dermoscopy) to confirm non-scarring autoimmune status.",
        provisional_summary_hi="अनंतिम निष्कर्ष: एलोपेसिया एरीटा के लक्षण। ट्राइकोस्कोपी (बालों की जांच) द्वारा सटीक पुष्टि की सलाह दी जाती है।"
    ),

    # ── 18. Cellulitis (Acute Bacterial) ──
    "cellulitis": ConditionSpec(
        condition_id="cellulitis",
        display_name="Cellulitis (Acute Deep Cutaneous Infection)",
        hindi_name="सेल्युलाइटिस (गंभीर बैक्टीरियल संक्रमण / Cellulitis)",
        icd10="L03",
        urgency=ClinicalUrgency.EMERGENCY,
        category="infectious_bacterial",
        is_dangerous_red_flag=True,
        required_history_evidence=["rapidly expanding warm painful red swelling over hours to 2 days", "fever, rigors, malaise", "portal of entry (scratch/crack/tinea)"],
        required_visual_morphology=["spreading poorly demarcated intense erythema, local edema, warmth, severe palpation tenderness"],
        predilection_sites=["lower leg / shin (unilateral)", "foot", "facial periorbital region", "forearm"],
        confirmatory_test_required="Blood Cultures, CBC, & Venous Duplex Ultrasound",
        confirmatory_test_description="Elevated CRP/ESR, leukocytosis with left shift; Duplex ultrasound is mandatory to exclude Deep Vein Thrombosis (DVT).",
        diagnostic_limitation="Stasis dermatitis vs unilateral cellulitis vs acute DVT cannot be determined safely without vascular ultrasound and acute inflammatory markers.",
        provisional_summary_en="EMERGENCY ALERT: Findings consistent with acute Cellulitis. Mandatory in-person emergency clinic visit for systemic antibiotic coverage and DVT ultrasound.",
        provisional_summary_hi="आपातकालीन चेतावनी: सेल्युलाइटिस (गंभीर संक्रमण) की संभावना। तुरंत नजदीकी अस्पताल के इमरजेंसी विभाग में दिखाएं।"
    ),

    # ── 19. Fixed Drug Eruption (FDE) ──
    "fixed_drug_eruption": ConditionSpec(
        condition_id="fixed_drug_eruption",
        display_name="Fixed Drug Eruption (FDE)",
        hindi_name="फिक्स्ड ड्रग इरप्शन (दवा की एलर्जी / FDE)",
        icd10="L27.0",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="drug_induced",
        required_history_evidence=["sudden onset 30 mins to 8 hours after taking an offending medication (e.g. cotrimoxazole, paracetamol, NSAIDs)", "recurs at exact same anatomical sites"],
        required_visual_morphology=["well-demarcated solitary or few circular dusky-red to violaceous macules", "central bulla or detachment", "resolves leaving deep slate-grey post-inflammatory hyperpigmentation"],
        predilection_sites=["glans penis / genitalia", "lips / oral mucosa", "hands", "feet", "perianal"],
        confirmatory_test_required="Detailed Medication Timeline & Oral/Patch Provocation Test",
        confirmatory_test_description="Systematic drug history correlation; patch testing at the site of prior resolved lesion with suspected drug.",
        diagnostic_limitation="Erythema multiforme vs solitary FDE vs bullous pemphigoid requires histopathology and medication rechallenge analysis.",
        provisional_summary_en="Provisional finding: Fixed Drug Eruption pattern. Recommended action: Immediately discontinue any non-essential painkiller or antibiotic under physician supervision.",
        provisional_summary_hi="अनंतिम निष्कर्ष: दवा की एलर्जी (FDE) के लक्षण। हाल ही में ली गई दवाओं की सूची लेकर तुरंत डॉक्टर को दिखाएं।"
    ),

    # ── 20. Pemphigus Vulgaris (Autoimmune Blistering) ──
    "pemphigus_vulgaris": ConditionSpec(
        condition_id="pemphigus_vulgaris",
        display_name="Pemphigus Vulgaris",
        hindi_name="पेम्फिगस वल्गेरिस (फफोलेदार रोग / Pemphigus Vulgaris)",
        icd10="L10.0",
        urgency=ClinicalUrgency.EMERGENCY,
        category="bullous_autoimmune",
        is_dangerous_red_flag=True,
        required_history_evidence=["painful non-healing oral erosions preceding skin blisters by months", "fragile blisters that rupture easily leaving raw denuded areas"],
        required_visual_morphology=["flaccid thin-roofed intraepidermal bullae on normal or erythematous skin", "positive Nikolsky sign (shearing pressure causes epidermal detachment)", "painful oral erosions"],
        predilection_sites=["oral buccal mucosa", "scalp", "chest", "intertriginous folds", "back"],
        confirmatory_test_required="Direct Immunofluorescence (DIF) & Anti-Desmoglein 1/3 ELISA",
        confirmatory_test_description="Perilesional punch biopsy for DIF showing intercellular IgG/C3 deposition in a 'fish-net' pattern throughout epidermis.",
        diagnostic_limitation="Pemphigus vulgaris vs bullous pemphigoid vs Stevens-Johnson syndrome cannot be treated without emergency histopathology and DIF.",
        provisional_summary_en="EMERGENCY ALERT: Flaccid blistering with Nikolsky sign suggests Pemphigus Vulgaris. Mandatory urgent dermatology hospitalization for DIF biopsy.",
        provisional_summary_hi="आपातकालीन चेतावनी: पेम्फिगस (फफोलेदार विकार) के लक्षण। तत्काल मेडिकल कॉलेज या बड़े अस्पताल के चर्म रोग विभाग में भर्ती हों।"
    ),

    # ── 21. Contact Dermatitis (Allergic / Irritant) ──
    "contact_dermatitis": ConditionSpec(
        condition_id="contact_dermatitis",
        display_name="Contact Dermatitis (Irritant / Allergic)",
        hindi_name="कॉन्टैक्ट डर्मेटाइटिस (संपर्क एलर्जी)",
        icd10="L23 / L24",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="inflammatory",
        required_history_evidence=["onset localized strictly to area of exogenous substance exposure (cement, hair dye, metal jewelry, detergents)", "burning or intense itching"],
        required_visual_morphology=["geometric, sharply demarcated erythematous vesicles, oozing, crusting, or fissuring conforming to contact shape"],
        predilection_sites=["hands (occupational)", "earlobes / neck (nickel jewelry)", "forehead / hairline (paraphenylenediamine hair dye)", "feet (footwear dermatitis)"],
        confirmatory_test_required="Comprehensive Patch Test (Indian Standard Series)",
        confirmatory_test_description="Application of standardized contact allergens in Finn chambers read at 48 and 72 hours for erythema/induration.",
        diagnostic_limitation="Cannot prove allergic vs irritant mechanism or identify specific culprit chemical without formal patch testing.",
        provisional_summary_en="Provisional finding: Contact Dermatitis pattern. Mandatory confirmatory test: Patch testing with Indian Standard Series to identify chemical trigger.",
        provisional_summary_hi="अनंतिम निष्कर्ष: कॉन्टैक्ट डर्मेटाइटिस (संपर्क एलर्जी)। एलर्जी का कारण जानने के लिए पैच टेस्ट करवाएं।"
    ),

    # ── 22. Furunculosis / Boils (Deep Bacterial) ──
    "furunculosis": ConditionSpec(
        condition_id="furunculosis",
        display_name="Furunculosis (Deep Bacterial Boils)",
        hindi_name="बालतोड़ / फुंसी (Furuncle / Boil)",
        icd10="L02",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="infectious_bacterial",
        required_history_evidence=["rapid onset over 1-3 days of painful throbbing lump", "history of friction, occlusion, or diabetes"],
        required_visual_morphology=["tender, erythematous, warm, fluctuant nodule centered around a hair follicle, developing central necrotic purulent core"],
        predilection_sites=["buttocks", "axillae", "groin / inner thighs", "neck / nape", "face (danger triangle)"],
        confirmatory_test_required="Purulent Exudate Gram Stain & Culture / Fasting Blood Glucose",
        confirmatory_test_description="Pus culture identifies Staphylococcus aureus and antibiotic sensitivities; fasting blood sugar screen for underlying diabetes mellitus.",
        diagnostic_limitation="Deep abscess vs epidermal inclusion cyst rupture vs hidradenitis suppurativa requires surgical evaluation and culture.",
        provisional_summary_en="Provisional finding: Furuncle / Cutaneous Abscess pattern. Recommended confirmatory test: Pus culture and fasting glucose assessment.",
        provisional_summary_hi="अनंतिम निष्कर्ष: बालतोड़ या गहरा फोड़ा (Furuncle)। मवाद की जांच व ब्लड शुगर टेस्ट की सलाह दी जाती है।"
    ),

    # ── 23. Miliaria (Prickly Heat / Heat Rash) ──
    "miliaria": ConditionSpec(
        condition_id="miliaria",
        display_name="Miliaria (Heat Rash / Prickly Heat)",
        hindi_name="घमौरियां (Miliaria / Prickly Heat)",
        icd10="L74.3",
        urgency=ClinicalUrgency.ROUTINE,
        category="sweat_gland",
        required_history_evidence=["sudden onset during intense heat and humidity or fever", "stinging / prickling sensation aggravated by sweating"],
        required_visual_morphology=["profuse uniform 1-2mm discrete erythematous papules or clear non-follicular vesicles (miliaria crystallina vs rubra)"],
        predilection_sites=["neck", "upper chest", "back", "flexural folds", "occluded clothing areas"],
        confirmatory_test_required="Clinical Evaluation / Dermoscopy",
        confirmatory_test_description="Dermoscopic identification of sweat duct occlusion with absence of follicular orientation.",
        diagnostic_limitation="Miliaria rubra vs viral exanthem vs pityrosporum folliculitis requires observation of rapid resolution in cool environment.",
        provisional_summary_en="Provisional finding: Miliaria (Prickly Heat) pattern. Recommended management: Cool environment, loose cotton clothing, avoid occlusive creams.",
        provisional_summary_hi="अनंतिम निष्कर्ष: घमौरियां (Heat Rash)। ठंडी व हवादार जगह पर रहें और सूती ढीले कपड़े पहनें।"
    ),

    # ── 24. Other / Reactive / Atypical Dermatosis ──
    "other_unclear": ConditionSpec(
        condition_id="other_unclear",
        display_name="Other / Atypical / Reactive Dermatosis",
        hindi_name="अन्य / अनिर्धारित त्वचा विकार",
        icd10="L99",
        urgency=ClinicalUrgency.SEEK_OPD,
        category="unclear_referral",
        required_history_evidence=["atypical onset", "mixed symptoms not conforming to standard single-entity presentations"],
        required_visual_morphology=["polymorphous, overlapping maculopapular, annular, or purpuric morphology"],
        predilection_sites=["variable"],
        confirmatory_test_required="Comprehensive Dermatological Biopsy and Serological Panel",
        confirmatory_test_description="4mm punch biopsy with H&E staining, DIF, complete autoimmune panel (ANA), and infectious serology.",
        diagnostic_limitation="Cannot be accurately triaged by visual inspection alone; requires multi-modal laboratory and histopathologic investigation.",
        provisional_summary_en="Provisional finding: Atypical / Reactive Dermatosis. Mandatory recommendation: In-person clinical examination and histopathological biopsy.",
        provisional_summary_hi="अनंतिम निष्कर्ष: अनिर्धारित त्वचा विकार। सटीक पहचान हेतु डॉक्टर से प्रत्यक्ष जांच व बायोप्सी करवाना आवश्यक है।"
    )
}


class ConditionRegistryService:
    """Service providing programmatic access to the expanded 24-condition ontology."""

    @classmethod
    def get_spec(cls, condition_key: str) -> ConditionSpec:
        key = condition_key.lower().strip()
        if key in EXPANDED_24_CONDITIONS:
            return EXPANDED_24_CONDITIONS[key]
        # Match aliases
        for k, spec in EXPANDED_24_CONDITIONS.items():
            if k in key or key in k:
                return spec
        return EXPANDED_24_CONDITIONS["other_unclear"]

    @classmethod
    def list_all(cls) -> List[ConditionSpec]:
        return list(EXPANDED_24_CONDITIONS.values())

    @classmethod
    def format_provisional_output(cls, condition_key: str, confidence: float, lang: str = "en") -> str:
        spec = cls.get_spec(condition_key)
        conf_pct = int(round(confidence * 100))
        if lang.startswith("hi"):
            return (
                f"अनंतिम निष्कर्ष: {spec.hindi_name} (अनुमानित संभावना: {conf_pct}%)। "
                f"पुष्टि हेतु अनिवार्य जांच: {spec.confirmatory_test_required}। "
                f"ध्यान दें: यह कोई अंतिम निदान नहीं है।"
            )
        else:
            return (
                f"Provisional finding: {spec.display_name} (Confidence: {conf_pct}%). "
                f"Confirmatory test required: {spec.confirmatory_test_required}. "
                f"Note: This is a screening assessment, not a definitive diagnosis."
            )

