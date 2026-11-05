# Clinical Error Taxonomy & Failure Mode Analysis (Track B)

This document catalogs the systematic failure modes of the AI system, points of dermatologist disagreement, and the targeted data acquisition required to resolve them.

---

## 1. Primary Failure Mode Classes

### Category A: Visual Mimics & Morphological Overlap
* **Example:** Tinea incognito (steroid-modified ringworm) presenting as poorly-demarcated eczematous patches.
* **Failure Mechanism:** Visual classifier relies on peripheral active annular scaling; topical steroids suppress redness and scale while fungi proliferate.
* **System Safeguard:** Tier 2 Head Agent directly inquires about prior OTC triple-combination steroid cream usage (*Quadriderm*, *Betnovate*), shifting Bayesian prior toward Tinea and mandating a **KOH preparation**.
* **Data Fix:** Collect 500+ confirmed Tinea incognito phone photos from Indian rural health centers.

### Category B: Melanin Masking in Fitzpatrick Types V & VI
* **Example:** Early erythema appearing violaceous, slate-grey, or hyperpigmented rather than classic pink/red.
* **Failure Mechanism:** Standard visual models trained on Caucasian cohorts under-detect mild inflammation without distinct redness.
* **System Safeguard:** Multi-spectral contrast stretching and prioritization of tactile pruritus and xerosis duration in history.
* **Data Fix:** Incorporate DDI (Diverse Dermatology Images) and Indian pilot data exclusively tagged for Types IV–VI.

### Category C: Complex Household Transmission Asynchrony
* **Example:** Scabies presenting in early infant or index patient before household members develop symptoms (incubation period: 3-6 weeks).
* **Failure Mechanism:** Negative household contact slot suppresses scabies prior if reliance is purely binary.
* **System Safeguard:** Anatomical web-space / nocturnal itch weighting overrides negative family history if symptoms duration is <3 weeks.
* **Data Fix:** Longitudinal cohort pilot tracking index cases over 30 days.

---

## 2. Dermatologist Disagreement Taxonomy
Where certified dermatologists disagree with each other on phone photos:
1. **Nummular Eczema vs. Tinea Corporis:** 14% inter-observer disagreement rate without fungal microscopy.
2. **Early Plaque Psoriasis vs. Lichen Simplex Chronicus:** Disagreement resolved only on extensor joint or nail pitting inspection.
3. **Mild Acneiform Folliculitis vs. Early Comedonal Acne:** Subjective boundary on non-dermoscopic photos.
