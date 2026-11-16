# MVP workflow and implementation status

## Current product direction

The default MVP is now independent provisional screening plus supported basic care, treatment information, and follow-up. Clinician approval is a future optional milestone, not a gate in the default UI. `apps/web/src/features.ts` keeps the reviewer workflow disabled. Its authenticated endpoints are retained for later use. Treatment overviews are not individualized prescriptions, and unknown/serious cases still retain an assessment/escalation path. The historical signed-plan workflow below applies only when that feature is enabled.

## Connected workflow

1. Start an English or Hindi encounter and complete voice/text history.
2. Upload a photo. The multimodal service selects provisional candidates from the 30-condition catalog.
3. Answer the candidate-specific question, confirm the history, and run screening.
4. Read the provisional screening and next step. Urgency and uncertainty remain visible.
5. Open Care plan & follow-up. The reviewer workspace shows draft treatment context and source links.
6. An authorized reviewer supplies their identity, assessment, patient instructions, follow-up, and return precautions; signing releases that exact text.
7. The patient refreshes plan status and reads or listens to the signed text.
8. A progress update records improvement, unchanged symptoms, deterioration, urgent symptoms, and examination completion. New information requires plan review.

The separate legacy brief approval action records review notes only. It does not authorize delivery of a treatment plan.

## Server setup

Set `QDOC_CLINICIAN_KEY` in the backend process environment to a strong random secret before starting the server. Supply that secret only to the reviewer. Do not put it in the frontend build, source control, URL, or a public demo slide. Signing fails closed when the key is missing. The reviewer form keeps the supplied key in component memory and clears it after successful signing.

Run the existing FastAPI server and frontend as described in README.md. A working multimodal provider credential is needed for expanded visual recognition; the local fallback remains narrower. Browser speech playback uses the signed plan's selected language without generating or translating medical instructions.

## State and persistence

`GET /api/v1/session/{id}/care` returns draft, signed, or needs_review status. The signing endpoint binds an immutable plan to a hash of the brief, patient turns, image records, and follow-up records. The signing transaction rejects stale evidence. New input makes the old plan unavailable as the current plan, while preserving its historical database record.

`POST /api/v1/session/{id}/care/sign` requires the reviewer credential. `POST /api/v1/session/{id}/care/follow-up` records new patient information. The UI refreshes after writes. Patient updates do not automatically modify medication instructions.

## Boundaries still requiring work before real clinical deployment

This is a connected prototype, not the entire production architecture proposal. Patient access still relies on possession of a session ID; complete patient authentication, tenant isolation, per-clinician identities and credential verification are not implemented. The shared reviewer key authenticates access to signing, not the professional identity typed in the form. Do not expose real patient data through a public deployment with this access model.

The 30-condition content remains draft. It includes recognition clues, one discriminating question per named condition in English/Hindi, basic care where available, treatment overviews, and referral scope. It is not a comprehensive drug database, examination protocol, or clinically validated diagnostic service. Patient-specific treatment is supplied by the reviewer. Condition-specific safety interpretation, full differential pathways, contraindication/interaction checking, licensed reference images, and local formulary work remain outstanding.

Follow-up recording and manual refresh are implemented; automated scheduling, notification delivery, referral booking, and external EHR integration are not. No messages are automatically sent. The interface does not guarantee a clinician response time.

## Verification

Run `python -m pytest tests/test_care_workflow.py tests/test_condition_coverage.py tests/test_screening_presentation.py tests/test_consultation.py -q` and `npm run build` from apps/web. These verify software behavior, including credential rejection, stale-plan rejection, follow-up invalidation, condition normalization, and screening presentation. They do not establish clinical accuracy or live provider availability.
