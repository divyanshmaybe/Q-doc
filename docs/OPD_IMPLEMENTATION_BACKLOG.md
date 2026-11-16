# Q-Doc implementation backlog

8 November 2026 • Proposed work; these changes have not been implemented

Read the [architecture](OPD_ARCHITECTURE_PROPOSAL.md) and [knowledge design](DERMATOLOGY_KNOWLEDGE_DESIGN.md) first. Priority is dependency order and clinical risk, not an estimated delivery date. Preserve the existing uncommitted application work when implementing.

Updated priority: the user selected breadth-first development before clinical validation. The first implemented breadth pass is documented in [current coverage](IMPLEMENTED_CONDITION_COVERAGE.md): 30 condition candidates plus two special categories, with draft care/treatment summaries and referral boundaries. The single-condition workflow milestone below remains a useful integration slice, but does not block catalog expansion. Clinical validation is a later milestone; software regression checks continue during development.

## First milestone: one complete supervised encounter

Deliver one adult acne assessment workflow, including an unclear presentation and an urgent interruption. The clinician can inspect evidence, correct it, decide whether more examination is needed, and sign a plan. The patient receives only the current signed plan. Clinical content cannot become active until its clinical review is complete.

| ID | Priority / owner | Concrete work | Acceptance evidence |
|---|---|---|---|
| QD-01 | P0 / clinical lead + product | Define intended use, adult eligibility, recognition/assessment/management scope, clinician responsibility, and escalation ownership | Versioned scope approved by accountable clinical owner; no broad doctor-replacement claim |
| QD-02 | P0 / engineering | Separate demonstration datasets/reports from clinical evaluation; label synthetic results; document model initialization and trained-artifact requirements | Reports declare data origin and actual inference path; missing trained artifact cannot yield an apparently validated result |
| QD-03 | P0 / clinical editor | Audit existing registry and treatments against source locations; quarantine unsupported mandatory tests and prescribing claims | Each existing claim has supported / revise / remove / unresolved status; no automatic migration to approved content |
| QD-04 | P0 / backend | Add provenance-bearing observations, explicit unknown states, lesion IDs, corrections, and encounter versions | Correcting a symptom preserves the previous observation and its origin; missing answer never becomes false |
| QD-05 | P0 / backend + clinical lead | Formalize safety transitions and approved interruption scripts independent of diagnosis generation | Urgent input interrupts routine questions even if vision, retrieval, or LLM calls fail; ambiguous safety input triggers clarification/escalation |
| QD-06 | P0 / backend | Enforce clinician roles and resource-level access; add version-bound plan signing and patient release gate | Patient cannot sign; another patient cannot access encounter; material new evidence blocks stale-plan delivery |
| QD-07 | P1 / knowledge engineering | Implement source, claim, condition, and release records; draft/approved separation; structured retrieval | Draft, suspended, and inapplicable records excluded; each retrieved recommendation resolves to an approved source locator |
| QD-08 | P1 / dermatologist + medication reviewer | Complete one locally adapted acne pathway and review all management prerequisites | Signed clinical content review; atypical/insufficient-evidence branches included; medication details verified independently |
| QD-09 | P1 / speech + frontend | Confirm consequential facts; fix ambiguous multi-question answers; support barge-in, text fallback, and resume | Interrupted audio cancels; correction updates correct fact; reconnection does not repeat or duplicate submitted turns |
| QD-10 | P1 / frontend + clinical lead | Build clinician evidence view with unknowns, photos, source links, competing hypotheses, and edit/sign actions | Reviewer can identify missing examination and decline to diagnose; signatures record reviewed version |
| QD-11 | P1 / backend + frontend | Deliver signed plan with validated language rendering and teach-back; record follow-up and referral status | Spoken and written instructions preserve signed meaning; deterioration returns to review; referral message is not marked completed care |
| QD-12 | P1 / clinical research + engineering | Run end-to-end offline evaluation with typical, misleading, unclear, and urgent cases | Software results separated from clinical review results; failures documented; no readiness claim based on synthetic accuracy |

QD-01–03 can progress alongside the technical foundations. QD-07–08 depend on the source/content decisions. QD-10–11 depend on observation provenance and authorization. Do not enable clinical delivery merely because the UI is finished.

## Next milestone: initial dermatology service

Expand to the core conditions in the knowledge design, one reviewed module at a time. Build contact/exposure history, serial images, condition-specific examination requests, investigation result reconciliation, and structured referral letters. Add clinician workload, queue-age, comprehension, cost, and outcome measurements.

Before a prospective pilot, establish licensed/consented case collection, independent adjudication, patient-level dataset separation, incident response, support coverage, retention rules, and vendor agreements. Clinical and statistical leads must specify the acceptance thresholds and study size before inspecting results.

## Suggested engineering acceptance scenarios

1. Patient reports two lesions with different timelines: images and questions stay attached to the correct lesion.
2. Speech transcription drops a negation: confirmation corrects the fact before it drives a consequential decision.
3. Patient changes an allergy after plan signing: old plan is not silently served as current.
4. A high-ranking hypothesis conflicts with a dangerous symptom: escalation takes precedence.
5. Photo is unusable after a bounded retake attempt: offer a clinician/examination path, without guessing.
6. No approved knowledge exists for the candidate condition: produce an evidence summary and knowledge gap, not invented guidance.
7. A retrieved document contains instructions to bypass review: it cannot change permissions or encounter state.
8. An approved claim is suspended: new drafts cannot use it, and affected active cases are flagged for clinical review.
9. A model proposes a valid-looking but nonexistent citation: reject the draft recommendation.
10. Clinician cannot determine diagnosis remotely: encounter can end in a useful examination/referral plan.
11. User speaks while TTS is playing: cancel stale audio before processing the correction.
12. No clinician is available: disclose queue status and the appropriate alternative route; never fabricate approval.

## Explicit external dependencies

Named Indian clinical ownership, locally applicable prescribing/formulary data, source reuse rights, bilingual clinical review, and real-case evaluation access are required to turn this design into a clinically approved service. They cannot be replaced with more generated medical text. Engineering can build the draft-content pipeline and encounter controls while these dependencies are arranged.
