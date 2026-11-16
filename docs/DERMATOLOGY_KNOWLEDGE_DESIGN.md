# Dermatology knowledge base: content, evidence, and release design

Draft for clinical review • 8 November 2026 • India adult supervised OPD

This document defines how to build a grounded knowledge base and supplies a researched starting point. It is not an exhaustive or clinically approved treatment database. The catalog below is a proposed content backlog; inclusion does not establish that a condition can be diagnosed remotely. Treatment summaries are clinician-facing design examples, not prescriptions. See [architecture proposal](OPD_ARCHITECTURE_PROPOSAL.md).

## 1. Define coverage properly

“Almost every common condition” needs a denominator: collect the diagnosis mix and presenting complaints from the intended clinics, then measure how many encounters have a reviewed pathway. Prioritize prevalence, harm from missing a diagnosis, diagnostic confusion, available evidence, and suitability for the service. Chronic conditions may be manageable without being curable.

Use three independent scopes:

* **Recognition scope:** patterns the system can flag, including dangerous and uncommon alternatives.
* **Assessment scope:** conditions with reviewed history, examination, differential, and test pathways.
* **Management scope:** conditions for which the local clinical team has approved treatment support.

A condition can be recognition-only. Pregnancy, immunosuppression, serious comorbidity, extensive disease, and failed treatment can move an otherwise common condition outside a routine pathway. Do not infer that a condition is uncomplicated solely because the patient's age is in scope.

## 2. Proposed coverage catalog

These are planning candidates, not prevalence rankings or reviewed clinical instructions. Every item needs source selection and clinician review before activation. Variants may share a parent record but require separate management branches.

| Group | Candidate condition records | Suggested rollout |
|---|---|---|
| Common inflammatory disease | Atopic dermatitis, irritant contact dermatitis, allergic contact dermatitis, seborrhoeic dermatitis, nummular eczema, dyshidrotic eczema, lichen simplex chronicus, xerosis | Initial core plus expansion |
| Papulosquamous disease | Plaque psoriasis, guttate psoriasis, inverse psoriasis, lichen planus, pityriasis rosea | Core plaque psoriasis; expand others |
| Acne and related disorders | Acne vulgaris, rosacea, periorificial dermatitis, drug-induced acneiform eruption, hidradenitis suppurativa | Acne first; explicit mimics and referral pathways |
| Fungal/yeast disease | Tinea corporis, cruris, pedis, manuum, faciei, capitis, onychomycosis, pityriasis versicolor, candidal intertrigo | Common skin sites first; scalp/nail and resistant disease as separate branches |
| Infestation and bites | Scabies, crusted scabies, pediculosis, arthropod-bite reactions | Scabies core; crusted disease escalation |
| Bacterial disease | Impetigo, folliculitis, furuncle/abscess, cellulitis/erysipelas, erythrasma, paronychia | Clinician-led assessment; escalate systemic illness |
| Viral disease | Warts, molluscum contagiosum, herpes simplex, herpes zoster | Expand with site/severity and immunosuppression checks |
| Wheals and drug eruptions | Acute urticaria, chronic urticaria, angioedema, uncomplicated drug eruption, fixed drug eruption | Urticaria core; severe reactions always considered separately |
| Pigment changes | Vitiligo, melasma, post-inflammatory hyperpigmentation, pityriasis alba, acanthosis nigricans | Expansion with mimics and appropriate systemic assessment |
| Hair/scalp/nails | Androgenetic alopecia, telogen effluvium, alopecia areata, scarring alopecia patterns, nail psoriasis, ingrown nail | Expansion; avoid assuming all nail change is fungal |
| Benign growths | Skin tags, seborrhoeic keratosis, epidermoid cyst, common melanocytic naevus, dermatofibroma | Clinician assessment; no image-only malignancy exclusion |
| India-relevant referral pathways | Suspected leprosy, cutaneous tuberculosis, cutaneous leishmaniasis, genital ulcer/STI syndromes | Recognition/referral before treatment support |
| Must-not-miss pathways | Anaphylaxis, severe drug reaction including SJS/TEN, DRESS, necrotising infection, severe cellulitis/sepsis, eczema herpeticum, eye-threatening herpes, erythroderma, generalized pustular disease, suspicious malignancy | Safety recognition from the first release; obtain dedicated approved sources for every rule |

Start with deeply reviewed pathways for acne, atopic dermatitis, contact dermatitis, seborrhoeic dermatitis, common tinea sites, scabies, urticaria, and plaque psoriasis. In parallel, review dangerous alternatives that can interrupt those pathways. Count reviewed variants honestly; splitting one disease into ten site labels does not demonstrate ten independent validated capabilities.

## 3. Knowledge layers

1. **Source library:** lawful source copies or permitted excerpts, metadata, access dates, versions, hashes, and rights. Public access is not permission to republish text or images.
2. **Atomic claims:** one scoped clinical proposition, linked to an exact section/table/page and the population to which it applies.
3. **Condition pathways:** clinical definition, presentations, questions, examination, differentials, investigation indications, management branches, and follow-up.
4. **Medication/formulary knowledge:** independent, structured drug safety and prescribing data localized to India and the clinic.
5. **Executable rules:** reviewed, testable conditions for safety, evidence sufficiency, management eligibility, and release.
6. **Patient communication:** clinically approved translations and explanations tied to the underlying claims and signed plan.

Keep condition knowledge, patient evidence, and model output separate. Never write a model's speculative explanation back into the approved knowledge base.

## 4. Source policy

Prefer applicable Indian national/specialty guidance and local formulary policies where verified. Supplement with reputable international guidelines, systematic reviews, and primary research. Do not presume that an international drug approval, dose regimen, access pathway, or OTC classification applies in India. Educational resources can support examination descriptions and patient explanations but should not be the sole authority for complex prescribing.

This research pass verified the linked sources below; it did not verify a comprehensive IADVL guideline collection or local formulary. Those are explicit gaps, not grounds to claim IADVL adherence. NICE/AAD/CDC statements must retain their setting and population. Conflicting recommendations require a clinician-authored local resolution, not model voting or silently selecting whichever text was retrieved first.

For each source record capture publisher, title, URL, document identifier, publication/update date when explicitly available, access date, jurisdiction, intended population, superseded status, license/reuse limits, and the full-document review status. Do not use a search engine's crawl date as the guideline publication date.

## 5. Proposed record contract

```yaml
condition_id: acne_vulgaris
record_version: 0.1.0
status: draft # draft | clinical_review | approved | suspended | retired
intended_use: clinician_decision_support
population: {age_min: 18, jurisdiction: IN, setting: supervised_opd}
recognition_scope: true
assessment_scope: false # only enabled after review
management_scope: false
terminology:
  preferred_name: Acne vulgaris
  aliases: []
  codes: [] # terminology system + edition + verified mapping
definition_claim_ids: []
history_questions: [] # concept, wording, rationale, discriminator, source IDs
examination_features: [] # modality, examiner, required/conditional, limitations
diagnostic_basis: [] # clinical/test-supported; not a universal mandatory test
investigations: [] # indication, purpose, limitations, result interpretation
lookalikes: [] # distinguishing facts, missing evidence, consequence of error
severity: [] # validated tool/version where appropriate, assessor requirements
red_flags: [] # explicit rule IDs, priority, route, approved message IDs
management_branches: [] # prerequisites, actions, contraindications, claim IDs
follow_up: [] # clinician-selected interval, response measures, failure actions
patient_content_ids: []
claim_ids: []
review: {clinical_reviewer: null, approved_at: null, review_due: null}
```

This is a contract illustration, deliberately inactive. Empty fields are not clinically valid content.

Each claim needs: `claim_id`, `text`, `claim_type`, `condition_ids`, `population`, `applicability`, `source_id`, `source_locator`, `supporting_excerpt_or_permitted_reference`, `recommendation_strength_as_reported`, `evidence_certainty_as_reported`, `exceptions`, `reviewer`, `review_status`, and `version`. Preserve “not stated” when a source does not grade evidence; do not manufacture GRADE ratings.

Each investigation needs: `purpose = diagnosis | exclusion | severity | pretreatment_safety | monitoring`, `indication`, `required_under_this_branch`, `sample_or_exam`, `performer`, `limitations`, and `result_interpretation`. This avoids confusing a safety blood test before treatment with a test needed to diagnose the disease.

Each medication branch needs independently verified product/formulation, dose/route/frequency/duration when applicable, population restrictions, contraindications, interactions, pregnancy/lactation rules, monitoring, escalation, local availability/status, and prescriber approval. Do not fill missing values from model memory. No production medication branches are provided in this proposal.

## 6. Important corrections to the existing registry

| Current pattern | Better clinical representation | Supporting source |
|---|---|---|
| Acne requires dermoscopy/comedone extraction | Clinical examination can diagnose acne; additional assessment depends on uncertainty | [AAD acne diagnosis](https://www.aad.org/public/diseases/acne/derm-treat/treat/) |
| Atopic dermatitis universally requires patch testing/total IgE | Clinical history and examination are central; additional tests are selected to investigate alternatives or relevant allergy | [AAD atopic dermatitis](https://www.aad.org/public/diseases/eczema/types/atopic-dermatitis/treatment) |
| Psoriasis universally requires punch biopsy | Examine skin, scalp, and nails and ask about joints; biopsy is sometimes used | [AAD psoriasis diagnosis](https://www.aad.org/public/diseases/psoriasis/treatment/treatment) |
| A field implies one test always settles diagnosis | Record conditional testing and uncertainty; an unavailable or negative test is not a universal rule-out | [CDC scabies](https://www.cdc.gov/scabies/about/) |

These are proposed content corrections. The existing Python records have not been changed or clinically approved in this work.

## 7. Researched starter pathway notes

The following concise notes illustrate the content direction. Clinical reviewers must turn them into precise, source-linked rules and verify all population restrictions. Suggested questions are design proposals, not validated diagnostic criteria.

### Acne vulgaris

Clinical anchor: clinician inspection can establish acne and distinguish lesion types. Treatment depends on the presentation. The AAD guideline supports several topical and systemic options and emphasizes limiting systemic antibiotic use and combining systemic antibiotics with benzoyl peroxide and other topical therapies. [Diagnosis](https://www.aad.org/public/diseases/acne/derm-treat/treat/) · [Guideline](https://www.aad.org/member/clinical-quality/guidelines/acne)

Proposed intake: sites, duration, previous treatment and response, current medications, scarring, impact, and relevant reproductive context before medication selection. Capture overview and focused lesion images. A clinician should distinguish acne from folliculitis, periorificial dermatitis, and other lookalikes. The treatment module should support severity-based selection and referral; systemic or pregnancy-sensitive treatment requires its own reviewed prerequisites. Do not use comedone extraction as a routine diagnostic requirement.

### Atopic dermatitis and eczema presentations

Clinical anchor: assessment uses skin examination and history; testing may help clarify selected cases. AAD guidance supports moisturizers and several anti-inflammatory topical options, with treatment choice dependent on the clinical setting. [Diagnosis](https://www.aad.org/public/diseases/eczema/types/atopic-dermatitis/treatment) · [Guideline](https://www.aad.org/member/clinical-quality/guidelines/atopic-dermatitis)

Proposed intake: itch, recurrence, distribution, sleep disturbance, exposures, treatment use, and signs of infection. Preserve “eczema pattern” separately from “atopic dermatitis.” The reviewer must distinguish contact dermatitis, infection, and other mimics. A management branch needs body-site, potency, duration, infection, and population safeguards before any topical steroid instructions. Do not label all eczema as allergy or make broad allergy testing mandatory.

### Psoriasis

Clinical anchor: examine skin, nails, and scalp; ask about joint symptoms. Biopsy is conditional rather than universal. [AAD diagnosis](https://www.aad.org/public/diseases/psoriasis/treatment/treatment)

Proposed intake: course, sites, prior diagnosis/treatment, joint symptoms, functional burden, and spread. The clinical reviewer should approve a severity instrument and escalation rules for extensive or unstable presentations. Treatment support needs a separately sourced local protocol; this research pass does not supply a psoriasis prescribing branch.

### Dermatophyte infection (tinea)

Clinical anchor: CDC recommends diagnostic testing before antifungal treatment and notes emerging resistant disease. It distinguishes skin, scalp, and nail presentations. [CDC clinical overview](https://www.cdc.gov/ringworm/hcp/clinical-overview/index.html)

Proposed intake: location, spread, contacts, prior antifungal use and response, and all applied creams. Ask about combination creams without assuming the patient knows their ingredients. The local pathway should specify when and how fungal testing is obtained and interpreted, especially for persistent disease. Site and extent must determine the treatment branch; recurrent or resistant disease needs clinician-led reassessment. A photograph cannot establish the organism or drug susceptibility.

### Scabies

Clinical anchor: history and examination can support assessment; clinicians may seek mites, eggs, or faeces for confirmation. CDC describes topical and oral treatment choices with population restrictions; US approval details must not be imported as Indian authorization. [Diagnosis](https://www.cdc.gov/scabies/about/) · [Clinical care](https://www.cdc.gov/scabies/hcp/clinical-care/index.html)

Proposed intake: itch timing, contacts with symptoms, sites, prior treatment, and whether close contacts were assessed. Collect relevant images where appropriate. Do not infer certainty from household itch alone. Management must include reviewed contact/environmental measures and a distinction between persistent symptoms, reinfestation, and treatment failure. Crusted disease needs a separate clinician escalation pathway. Doses and application instructions require local clinical approval.

### Urticaria/angioedema

Clinical anchor: individual hives usually disappear within 24 hours even when new lesions continue appearing. Swelling affecting the airway or breathing requires emergency assessment. [AAD symptoms](https://www.aad.org/public/diseases/a-z/hives-symptoms) · [NHS hives](https://www.nhs.uk/conditions/hives/?src=conditionswidget)

Proposed intake: first ask about breathing/swallowing and sudden swelling, then the duration of one lesion, recurrence, exposures, medications, and systemic symptoms. Time-separated photographs may help describe transience. Persisting, painful, or otherwise atypical lesions need clinician reassessment rather than a forced urticaria label. A locally reviewed medication pathway is still required.

### Impetigo and cellulitis

Clinical anchor: NICE differentiates impetigo management by extent, bullous disease, systemic illness, and complication risk. Its cellulitis guidance identifies hospital referral for suspected serious complications and additional concerns around the eye/nose and severe illness. These are UK recommendations and require local antimicrobial adaptation. [Impetigo](https://www.nice.org.uk/guidance/ng153/chapter/Recommendations) · [Cellulitis](https://www.nice.org.uk/guidance/ng141/chapter/Recommendations)

Proposed intake: progression, pain, fever/systemic symptoms, site, relevant injury, immune status, and prior treatment. Remote images do not establish palpation findings or reliably exclude a deeper infection. Route potentially serious disease promptly to clinician/in-person assessment. Do not generate an antibiotic regimen from the disease label alone.

### Leprosy recognition pathway

Clinical anchor: WHO describes characteristic sensory loss in a skin patch, peripheral nerve findings, or bacilli in a smear as cardinal diagnostic signs. This illustrates why a pigment-only image classifier is inadequate. [WHO leprosy](https://www.who.int/news-room/fact-sheets/detail/leprosy/)

Proposed intake: reported altered sensation, weakness, duration, and lesions not behaving as expected. Route suspected cases for a trained clinical examination; do not ask patients to perform sharp-object or heat testing. This is recognition/referral scope, not a treatment module.

### Severe drug reaction recognition pathway

Clinical anchor: SJS may involve a serious medication-associated reaction with systemic symptoms, rash, and peeling. [NHS SJS](https://www.nhs.uk/conditions/stevens-johnson-syndrome/)

Proposed system behavior: a concerning combination of new medication exposure, painful/blistering/peeling rash, or mucosal symptoms must interrupt routine intake and invoke a clinician-approved urgent pathway. A complete rule set and localized action scripts require dedicated clinical review. Do not wait for a confident disease classification.

## 8. How agents should use the knowledge

Retrieval sequence:

1. Resolve the presenting problem and candidate concepts without forcing one diagnosis.
2. Filter by approved release, jurisdiction/local adaptation, population, intended use, and modality.
3. Retrieve structured safety/evidence requirements, then relevant claim text with lexical/semantic search as needed.
4. Include competing hypotheses and dangerous alternatives; do not retrieve only evidence supporting the leading hypothesis.
5. Ask a bounded next question or request an examination when it could change the decision.
6. Produce a structured clinician draft referencing observation IDs and claim IDs.
7. Verify citations resolve, claims actually support the proposed action, prerequisites are met, and no source conflict is concealed.
8. Submit to clinician review. Only the signed, current plan reaches the patient.

A vector database is an index, not the authority. Similarity is not clinical relevance or truth. A citation checker that only confirms a URL exists is insufficient. The system must test whether the recommendation is supported for this patient and this setting.

Use live web search only in a controlled knowledge-maintenance process. Unreviewed results do not enter active encounters. If the approved KB lacks a needed pathway, surface that gap and route to the clinician; do not answer from unrestricted model memory.

## 9. Knowledge production and release workflow

`source discovery → rights check → source snapshot → draft extraction → claim verification → clinical review → India/local adaptation → translation review → regression evaluation → signed release → monitoring`

Recommended governance: a dermatologist owns condition content; a qualified prescriber/pharmacist reviews medication branches; bilingual clinical reviewers approve translations; an engineering owner verifies executable rules and release integrity. This staffing is a proposal, not a claim that reviews have occurred.

Require independent review of high-risk rules and prescribing logic. Track reviewer identity, disagreements, and resolution. Unresolved conflicts block the affected branch. An approval can cover a specific version only.

Proposed maintenance cadence: monitor high-priority sources monthly, review active modules at least annually, and trigger immediate assessment for safety alerts, source withdrawal, major guideline changes, or incidents. Adapt cadence to risk and resources. A missed review must not silently extend approval; suspend affected recommendations while retaining safe routing.

Store a release manifest with approved record IDs/hashes, source versions, policy version, approvers, effective date, and rollback target. Pin every encounter draft to its knowledge release. A release change should generate an impact list for affected active plans for clinical review, not silently rewrite prescriptions.

## 10. Acceptance checks before a module is called grounded

* Every actionable recommendation and safety rule has a verified source location and applicability statement.
* Every required test has an explicit indication; diagnostic and treatment-monitoring tests are distinguished.
* Every important lookalike has a next discriminator or an explicit referral boundary.
* Missing/uncertain facts do not become absent findings; multiple conditions can coexist.
* Medication guidance is complete enough for its intended use and independently reviewed; unfilled prerequisites block release.
* Patient language preserves uncertainty and the clinician's signed instructions.
* Cases cover typical, atypical, darker-skin appearances, misleading histories, prior treatment, missing images, and dangerous alternatives.
* Tests exercise patient instructions trying to override the protocol, malicious source text, fabricated citations, expired records, and provider outages.
* The clinical lead signs the release; engineering validation alone never marks it clinically valid.

## 11. Concrete next content deliverables

1. A source ledger and claim-level audit of the current three knowledge modules.
2. An approved recognition/escalation package before routine condition management.
3. One complete acne pathway demonstrating the entire record format and clinician workflow.
4. An initial core set expanded condition by condition with review evidence, not bulk generated prose.
5. A local medication/formulary dataset and explicit clinical ownership.
6. A clinician-authored evaluation set including mimics and insufficient-evidence cases.
7. A coverage report separating proposed, drafted, reviewed, approved, and clinically evaluated conditions.

The durable advantage is the ability to show exactly which evidence supports each decision, what remains unknown, and who approved the care plan.
