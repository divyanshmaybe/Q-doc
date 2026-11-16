# Consultation improvements and validation

The consultation now uses explicit history, clarification, photo, summary, assessment,
follow-up and handoff actions. Session snapshots store verbatim conversation turns,
reported/denied fact status, corrections and unresolved clarification requests.

Essential checks cannot be skipped by asking for treatment. A photo is optional;
without one the patient is directed to an examination. Confirmation of the history is
required before image analysis. Intake red flags preempt image quality and ordinary
questioning. Configured probability and margin thresholds are enforced, and session
operating mode is respected.

Patient-facing assessment wording is assembled by the policy layer. Existing treatment
knowledge is not marked clinician-approved: no generated medication plan is released
through the new assessment response. A clinician must review medication protocols,
contraindications, referral urgency and follow-up timing before deployment.

Voice changes include cancellation tokens for speech playback, preservation of text
across recognition restarts, extra time for hesitation, and waiting for the recorder's
last chunk. Interruption currently uses the microphone/orb tap or typed submission;
automatic hands-free interruption during loudspeaker playback needs acoustic echo
cancellation and device testing and is not implemented.

A temperature default of 1.28 is a scaling parameter, not proof of calibration.
Validate ECE/Brier score and reliability diagrams on held-out, representative data.
A change in model confidence or ranking after history is not measured diagnostic
improvement. Compare image-only and multimodal outcomes against independent labels,
report subgroup results and referral errors, and obtain clinician review of cases.

Regression scenarios are in tests/test_consultation.py. They run without provider
calls. Live Hindi/Hinglish STT, noisy-room timing, clinical accuracy, consent/storage
policies, and end-to-end kiosk hardware still require prospective validation.
