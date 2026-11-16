# Implemented draft condition coverage

8 November 2026

The multimodal recognition catalog now contains 30 named conditions and two special categories. This is software scope, not measured diagnostic performance. The local image classifier still has six disease classes and two special outputs. The expanded path requires a working multimodal provider.

Each record has candidate recognition clues, a clinician-facing treatment overview, basic care where available, and a management boundary. Legacy recognition clues remain explicitly unreviewed. Source links are not claim-level clinical approval. No doses or autonomous prescribing were added. English draft summaries are exposed in the clinician brief; complete condition-specific Hindi translation remains outstanding.

API: `GET /api/v1/conditions` exposes the catalog and classifier distinction.

| Condition | Management boundary | Basic-care notes |
|---|---|---|
| Acne Vulgaris | basic care and review | Available |
| Eczema (Atopic Dermatitis) | basic care and review | Available |
| Psoriasis Vulgaris | basic care and review | Available |
| Tinea (Dermatophytosis / Ringworm) | basic care and review | Available |
| Urticaria (Hives / Wheals) | basic care and review | Available |
| Scabies Infestation | clinician review | Clinician assessment first |
| Suspicious Cutaneous Lesion (Possible Malignancy) | refer | Clinician assessment first |
| Seborrheic Dermatitis | clinician review | Clinician assessment first |
| Lichen Planus | clinician review | Clinician assessment first |
| Vitiligo | basic care and review | Available |
| Pityriasis Versicolor (Tinea Versicolor) | clinician review | Clinician assessment first |
| Pityriasis Rosea | clinician review | Clinician assessment first |
| Impetigo (Bacterial Pyoderma) | clinician review | Clinician assessment first |
| Herpes Zoster (Shingles) | refer | Clinician assessment first |
| Melasma (Chloasma) | basic care and review | Available |
| Verruca Vulgaris (Common Viral Warts) | basic care and review | Available |
| Alopecia Areata | clinician review | Clinician assessment first |
| Cellulitis (Acute Deep Cutaneous Infection) | refer | Clinician assessment first |
| Fixed Drug Eruption (FDE) | refer | Clinician assessment first |
| Pemphigus Vulgaris | refer | Clinician assessment first |
| Contact Dermatitis (Irritant / Allergic) | basic care and review | Available |
| Furunculosis (Deep Bacterial Boils) | clinician review | Available |
| Miliaria (Heat Rash / Prickly Heat) | basic care and review | Available |
| Other / Atypical / Reactive Dermatosis | refer | Clinician assessment first |
| Acanthosis nigricans | clinician review | Clinician assessment first |
| Rosacea | basic care and review | Available |
| Folliculitis | basic care and review | Available |
| Dry skin (xerosis) | basic care and review | Available |
| Keratosis pilaris | basic care and review | Available |
| Molluscum contagiosum | basic care and review | Available |
| Possible fungal nail infection | clinician review | Available |
| Suspected leprosy | refer | Clinician assessment first |

## What changed

- The early-photo and final multimodal prompts receive the same catalog.
- Exact aliases replace substring matching; an unsupported label maps to other/unclear.
- New condition names survive parsing even when their score is below the baseline classifier score.
- The clinician brief includes structured care, treatment, scope, and source metadata.
- Referral-only conditions route to clinician assessment regardless of a high model score.
- Model-generated treatment prose is not used for the expanded multimodal treatment summary.

## Remaining work

Expand the catalog further using the design backlog; add condition-specific dynamic intake, differential/examination details, contraindication branches, bilingual care text, and local formulary rules. Clinical validation remains a later milestone. Basic software regression tests are run during development. A source-linked draft treatment overview is not a complete prescribing protocol.
