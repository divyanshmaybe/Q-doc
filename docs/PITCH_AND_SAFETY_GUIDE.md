# Q-Doc Pitch, Regulatory & Safety Guide

## What to Say in the Pitch (Section 12)

### ✅ What to Say:
> *"Q-Doc is autonomy-capable on a narrow set of common skin conditions, with measured accuracy, calibrated confidence, and a policy layer that controls when it acts alone."*

### ❌ What NOT to Say:
- Do NOT say: *"Autonomous diagnosis deployed"*
- Do NOT say: *"Replaces the doctor"*
- Do NOT say: *"Clinically validated for all populations"*

### The Regulatory Anchor:
The claim that holds up legally and scientifically is that **autonomy is a configurable setting unlocked condition-by-condition as clinical evidence matures**. This mirrors the FDA approval pathway paved by **LumineticsCore** (formerly IDx-DR), which earned de novo authorization for diabetic retinopathy autonomous screening under strict operational constraints and referral thresholds.

---

## Risks and Mitigations (Section 11)

| Risk | Mitigation Implemented in Q-Doc |
|---|---|
| **Public images differ from phone photos** | Tested on smartphone-style image benchmarks (SCIN/DDI) with domain-gap checks and Laplacian variance filtering. |
| **Skin tone bias** | Stratified evaluation reporting separate metrics and 95% confidence intervals across Fitzpatrick skin types I-II, III-IV, and V-VI. |
| **Hallucinated reasoning** | Enforced closed 8-condition list, structured JSON extraction, and strict rule that citations must quote patient voice inputs. |
| **Speech recognition errors on medical terms** | Built-in cheap **Confirmation Turn** repeating key duration and site facts back to patient before image analysis. |
| **Medical device regulations** | Clear disclaimer framing as an investigational screening aid. Guidance planned through institutional incubation and CDSCO regulatory frameworks. |
| **Patient privacy** | Synthetic and volunteer demo data only. Architecture designed for Digital Personal Data Protection (DPDP) Act compliance. |
| **Accidental prescription of medicines** | Strict `never_output` policy layer sanitizer stripping all drug dosages, tablet counts, and prescription names. |

