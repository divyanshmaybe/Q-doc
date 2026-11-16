"""Breadth-first, draft recognition catalog; not a validated diagnostic model.

Legacy morphology is reused as candidate clues, never as mandatory criteria.
Treatment summaries are clinician-facing and do not authorize prescribing.
"""
import re
from copy import deepcopy

from services.clinical_knowledge.condition_registry import EXPANDED_24_CONDITIONS


def _key(value):
    return re.sub(r"[^a-z0-9]+", "_", str(getattr(value, "value", value)).lower()).strip("_")


CATALOG = {}
for legacy_id, spec in EXPANDED_24_CONDITIONS.items():
    condition_id = "acne" if legacy_id == "acne_vulgaris" else legacy_id
    CATALOG[condition_id] = {
        "condition_id": condition_id,
        "display_name": spec.display_name,
        "name_hi": spec.hindi_name,
        "recognition_clues": list(spec.required_visual_morphology),
        "history_clues": list(spec.required_history_evidence),
        "sites": list(spec.predilection_sites),
        "content_status": "draft",
        "recognition_provenance": "legacy_registry_unreviewed",
        "basic_care": [],
        "treatment_summary": "Clinician assessment is needed to select treatment.",
        "management_scope": "clinician_review",
        "referral_priority": "routine",
        "sources": [],
    }


def _add(condition_id, name, clues, question, source):
    CATALOG[condition_id] = {
        "condition_id": condition_id, "display_name": name, "name_hi": name,
        "recognition_clues": clues, "history_clues": [question], "sites": [],
        "content_status": "draft", "recognition_provenance": "source_linked_draft",
        "basic_care": [], "treatment_summary": "Clinician assessment is needed to select treatment.",
        "management_scope": "clinician_review", "referral_priority": "routine",
        "sources": [source],
    }


_add("acanthosis_nigricans", "Acanthosis nigricans",
     ["darkened, thickened, velvety skin in folds"],
     "Ask about onset and metabolic history; texture requires clinical correlation.",
     "https://www.nhs.uk/conditions/acanthosis-nigricans/")
_add("rosacea", "Rosacea", ["central facial flushing or persistent colour change", "acne-like facial bumps"],
     "Ask about flushing triggers and eye symptoms.", "https://www.nhs.uk/conditions/rosacea/")
_add("folliculitis", "Folliculitis", ["small bumps or pustules centered on hair follicles"],
     "Ask about shaving, friction, hot-tub exposure, and systemic symptoms.",
     "https://www.aad.org/public/diseases/a-z/folliculitis")
_add("xerosis", "Dry skin (xerosis)", ["dry, rough or flaky skin"],
     "Ask about duration, products, bathing habits, and persistent generalized itch.",
     "https://www.aad.org/public/everyday-care/skin-care-basics/dry/dermatologists-tips-relieve-dry-skin")
_add("keratosis_pilaris", "Keratosis pilaris", ["small rough follicular bumps, often upper arms or thighs"],
     "Ask about persistence, dryness, and whether bumps are painful or inflamed.",
     "https://www.nhs.uk/conditions/keratosis-pilaris/")
_add("molluscum_contagiosum", "Molluscum contagiosum", ["small raised bumps with a central depression"],
     "Ask about site, spread, immune suppression, and eye or genital involvement.",
     "https://www.nhs.uk/conditions/molluscum-contagiosum/")
_add("onychomycosis", "Possible fungal nail infection", ["thickened, discoloured or crumbly nails"],
     "Ask about nail trauma, psoriasis, diabetes, and immune suppression.",
     "https://www.nhs.uk/conditions/fungal-nail-infection/")
_add("suspected_leprosy", "Suspected leprosy", ["pale or reddish patch with reported altered sensation"],
     "Ask about numbness or weakness; arrange trained examination, not home sensation testing.",
     "https://www.who.int/news-room/fact-sheets/detail/leprosy/")


def _care(condition_id, care, treatment, source=None, scope="basic_care_and_review", priority="routine"):
    record = CATALOG[condition_id]
    record.update(basic_care=care, treatment_summary=treatment,
                  management_scope=scope, referral_priority=priority)
    if source and source not in record["sources"]:
        record["sources"].append(source)


_care("acne", ["Use gentle cleansing; avoid picking lesions."],
      "Topical treatment selection depends on lesion type and severity; consider benzoyl peroxide or a topical retinoid after contraindication review. Severe or scarring acne needs clinician-led escalation.",
      "https://www.aad.org/member/clinical-quality/guidelines/acne")
_care("eczema", ["Use a fragrance-free moisturizer and avoid irritating products."],
      "Emollient care plus clinician-selected anti-inflammatory treatment; site, infection, and severity affect selection.",
      "https://www.aad.org/member/clinical-quality/guidelines/atopic-dermatitis")
_care("psoriasis", ["Avoid scratching and keep dry skin moisturized."],
      "Clinician selects site- and severity-specific topical treatment; assess joints and extensive disease.",
      "https://www.aad.org/member/clinical-quality/guidelines/psoriasis")
_care("tinea", ["Keep affected areas clean and dry; avoid sharing towels."],
      "Confirm the fungal diagnosis as appropriate before selecting an antifungal; scalp, nail, extensive, or recurrent disease requires a separate assessment.",
      "https://www.cdc.gov/ringworm/hcp/clinical-overview/index.html")
_care("urticaria", ["Avoid known triggers and overheating."],
      "Clinician selects symptom treatment after checking airway symptoms, medication history, and atypical lesions.",
      "https://www.nhs.uk/conditions/hives/")
_care("scabies", [],
      "Clinician selects a scabicide and a coordinated contact/environmental plan; hygiene alone does not treat infestation.",
      "https://www.cdc.gov/scabies/hcp/clinical-care/index.html", scope="clinician_review")
_care("vitiligo", ["Protect affected skin from sunburn."],
      "Confirm the cause of pigment loss; treatment depends on extent, site, and progression.",
      "https://www.aad.org/public/diseases/a-z/vitiligo-treatment")
_care("melasma", ["Use sun protection and avoid irritating bleaching mixtures."],
      "Clinician selects pigment treatment after reviewing pregnancy status and competing diagnoses.",
      "https://www.aad.org/public/diseases/a-z/melasma-treatment")
_care("contact_dermatitis", ["Avoid a suspected irritating product; use gentle skin care."],
      "Identify the exposure; clinician selects anti-inflammatory treatment and whether patch testing is indicated.",
      "https://www.nhs.uk/conditions/contact-dermatitis/")
_care("seborrheic_dermatitis", [],
      "Clinician may select an antifungal shampoo or topical therapy according to the site and severity.",
      "https://www.aad.org/public/diseases/a-z/seborrheic-dermatitis-treatment", scope="clinician_review")
_care("lichen_planus", [], "Clinician assessment, especially for oral/genital or persistent disease, before anti-inflammatory treatment.",
      "https://www.nhs.uk/conditions/lichen-planus/", scope="clinician_review")
_care("pityriasis_versicolor", [], "Clinician selects topical antifungal treatment after distinguishing other causes of pigment change.",
      "https://www.pcds.org.uk/clinical-guidance/pityriasis-versicolor", scope="clinician_review")
_care("pityriasis_rosea", [], "Often self-limiting; confirm the pattern and consider itch relief. Pregnancy or atypical features require specific review.",
      "https://www.aad.org/public/diseases/a-z/pityriasis-rosea-treatment", scope="clinician_review")
_care("impetigo", [], "Clinician selects treatment based on extent, bullae, systemic symptoms, and local antimicrobial policy.",
      "https://www.nice.org.uk/guidance/ng153/chapter/Recommendations", scope="clinician_review", priority="prompt")
_care("herpes_zoster", [], "Prompt clinician assessment for antiviral eligibility and pain control; eye involvement needs urgent assessment.",
      "https://www.nhs.uk/conditions/shingles/", scope="refer", priority="prompt")
_care("verruca_vulgaris", ["Avoid picking or cutting the growth; do not share towels."],
      "After confirming a wart, consider observation or clinician-selected treatment. Face/genital or changing lesions need assessment before treatment.",
      "https://www.nhs.uk/conditions/warts-and-verrucas/")
_care("alopecia_areata", [], "Confirm the type of hair loss; observation or clinician-selected treatment depends on extent and impact.",
      "https://www.aad.org/public/diseases/hair-loss/types/alopecia/treatment", scope="clinician_review")
_care("cellulitis", [], "Prompt in-person assessment for antibiotics and severity; systemic illness or eye involvement may need emergency care.",
      "https://www.nice.org.uk/guidance/ng141/chapter/Recommendations", scope="refer", priority="prompt")
_care("fixed_drug_eruption", [], "Review the medication timeline with a clinician; do not rechallenge a suspected trigger to test the diagnosis.",
      "https://pcds.org.uk/clinical-guidance/adverse-cutaneous-drug-reactions-mild-to-moderate", scope="refer", priority="prompt")
_care("pemphigus_vulgaris", [], "Blistering or mucosal disease needs specialist examination and directed treatment.",
      "https://www.nhs.uk/conditions/pemphigus-vulgaris/", scope="refer", priority="prompt")
_care("furunculosis", ["Do not squeeze or pierce boils."],
      "Clinician assesses drainage, antibiotics, recurrence, and risk factors; systemic illness requires prompt care.",
      "https://www.nhs.uk/conditions/boils/", scope="clinician_review", priority="prompt")
_care("miliaria", ["Keep the skin cool; wear loose clothing and reduce sweating."],
      "Cooling and avoidance of overheating are basic care; persistent or worsening symptoms need reassessment.",
      "https://www.nhs.uk/conditions/heat-rash-prickly-heat/")
_care("acanthosis_nigricans", [], "Assess potential underlying causes; avoid assuming the pigmentation is dirt or treating it with harsh scrubbing.", scope="clinician_review")
_care("rosacea", ["Avoid personal flushing triggers and irritating products; use sun protection."],
      "Clinician selects treatment by symptoms; ask about eye symptoms before routine management.")
_care("folliculitis", ["Pause shaving or friction over affected skin."],
      "Mild cases may improve after removing the trigger; persistent or extensive disease needs assessment before antimicrobial treatment.")
_care("xerosis", ["Use fragrance-free moisturizer and short lukewarm washes."],
      "Barrier care is the initial approach; persistent or generalized symptoms need assessment for other causes.")
_care("keratosis_pilaris", ["Moisturize and avoid harsh scrubbing."],
      "Gentle skin care is a reasonable initial approach after confirming the pattern.")
_care("molluscum_contagiosum", ["Avoid squeezing or picking spots and sharing towels."],
      "Observation may be appropriate; adult genital, eye-adjacent, extensive, or immunocompromised presentations need specific clinician assessment.")
_care("onychomycosis", ["Keep feet clean and dry; do not share nail tools."],
      "Confirm fungal infection and review contraindications before systemic treatment; not all nail dystrophy is fungal.", scope="clinician_review")
_care("suspected_leprosy", [], "Arrange trained skin and nerve examination and program-specific care; do not diagnose or treat from a photograph alone.", scope="refer", priority="prompt")
_care("possible_malignancy", [], "Prompt dermatologist assessment; further examination or biopsy is selected by the clinician.", scope="refer", priority="prompt")
_care("other_unclear", [], "Clinical examination is needed; no condition-specific treatment is supported.", scope="refer")

ALIASES = {key: key for key in CATALOG}
ALIASES.update({_key(record["display_name"]): key for key, record in CATALOG.items()})
ALIASES.update({
    "acne_vulgaris": "acne", "atopic_dermatitis": "eczema", "psoriasis_vulgaris": "psoriasis",
    "ringworm": "tinea", "tinea_corporis": "tinea", "tinea_cruris": "tinea", "tinea_pedis": "tinea",
    "hives": "urticaria", "seborrhoeic_dermatitis": "seborrheic_dermatitis", "dandruff": "seborrheic_dermatitis",
    "tinea_versicolor": "pityriasis_versicolor", "shingles": "herpes_zoster", "warts": "verruca_vulgaris",
    "common_wart": "verruca_vulgaris", "boils": "furunculosis", "heat_rash": "miliaria",
    "prickly_heat": "miliaria", "dry_skin": "xerosis", "fungal_nail_infection": "onychomycosis",
    "leprosy": "suspected_leprosy", "hansen_disease": "suspected_leprosy",
    "other_or_unclear": "other_unclear", "unknown": "other_unclear", "unclear": "other_unclear",
})


def normalize_condition(value):
    """Exact aliases only: never turn 'not acne' or an empty string into acne."""
    return ALIASES.get(_key(value), "other_unclear")


def get_coverage(value):
    return deepcopy(CATALOG[normalize_condition(value)])


def catalog_prompt():
    return "\n".join(
        f"{key}: {record['display_name']}; candidate clues: {'; '.join(record['recognition_clues'][:2])}; "
        f"history: {'; '.join(record['history_clues'][:1])}; management: {record['management_scope']}"
        for key, record in CATALOG.items()
    )
