# Q-Doc MVP: Voice-First & Photo Skin Screening Agent

> Implementation following the **CODING AGENT DIRECTIVE: Q-DOC MVP BUILD GUIDE**.
> Voice-native clinical intake in Hindi/English, skin photo capture with blur/exposure rejection, multimodal constrained LLM/Bayesian reasoning over closed taxonomy, controllable autonomy policy layer, and 1-page clinician summaries.

---

## 🏗 Project Architecture & Directory Layout

```
qdoc-mvp/
├── README.md
├── pyproject.toml
├── docker-compose.yml
├── .env.example
├── config/
│   └── policy.yaml                # Editable safety rules & thresholds
├── services/
│   ├── api/
│   │   ├── main.py                # FastAPI entry point
│   │   ├── database.py            # SQLite schema (WAL mode) / Postgres
│   │   ├── models/
│   │   │   └── schema.py          # DB ORM models
│   │   └── routers/
│   │       ├── session.py         # /api/v1/session/start, /session/{id}, /admin/mode
│   │       ├── intake.py          # /api/v1/session/{id}/turn (slot-filling)
│   │       ├── analysis.py        # /api/v1/session/{id}/photo, /analyze
│   │       └── brief.py           # /api/v1/session/{id}/brief (clinician view)
│   ├── gateway/
│   │   ├── base.py                # Abstract adapters (BaseSTTAdapter, BaseTTSAdapter, BaseLLMAdapter)
│   │   ├── stt.py                 # Sarvam STT adapter + WebSpeech fallback
│   │   ├── tts.py                 # Sarvam TTS adapter (hi-IN, en-IN)
│   │   └── llm.py                 # LiteLLM / Anthropic / OpenAI / Gemini adapter
│   ├── dialogue/
│   │   ├── manager.py             # Slot-filling state machine & turn controller
│   │   └── schemas.py             # Intake slots Pydantic models & closed condition enum
│   ├── ml/
│   │   ├── classifier.py          # PyTorch inference wrapper (ConvNeXt/ViT)
│   │   ├── quality.py             # Blur (<100 laplacian var) & exposure rejection
│   │   └── calibrator.py          # Temperature scaling module (T=1.28)
│   ├── reasoner/
│   │   ├── engine.py              # Multimodal Bayesian-style clinical reasoner
│   │   └── prompts.py             # Strict constrained reasoning prompts
│   └── policy/
│       ├── evaluator.py           # Safety checks, abstention, red-flags
│       └── rules.py               # Policy loader & dosage sanitizer
├── apps/
│   └── web/                       # React / Vite mobile-first PWA
│       ├── src/
│       │   ├── components/
│       │   │   ├── VoiceRecorder.tsx
│       │   │   ├── CameraCapture.tsx
│       │   │   ├── ChatInterface.tsx
│       │   │   └── ClinicianBrief.tsx
│       │   ├── services/api.ts
│       │   └── App.tsx
│       ├── index.html
│       ├── app.js
│       └── styles.css
├── eval/
│   ├── datasets/                  # Held-out benchmark dataset
│   ├── run_benchmarks.py          # Stratified test set runner
│   └── metrics.py                 # Wilson CI, ECE, & recall calculators
├── tests/
│   ├── test_directive_checklist.py # All 5 Section 6 checklist test cases
│   ├── test_api_v1.py             # All API v1 endpoint integration tests
│   ├── test_policy.py             # Policy evaluator unit tests
│   └── test_reasoner.py           # Reasoner & closed taxonomy tests
└── run_tests.py                   # Standalone test runner
```

---

## 🔒 Closed Condition Scope (Taxonomy)

The diagnosis engine strictly enforces this closed enum (`services/dialogue/schemas.py`):
1. `eczema` (Atopic Dermatitis)
2. `psoriasis` (Psoriasis Vulgaris)
3. `acne` (Acne Vulgaris)
4. `urticaria` (Hives / Allergic Wheals)
5. `tinea` (Ringworm / Fungal Infection)
6. `scabies` (Scabies Infestation)
7. `other_unclear` (Referral class)
8. `possible_malignancy` (Hard red-flag class: always refers, never reassures)

---

## ⚡ FastAPI v1 Endpoints Contract

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/session/start` | Creates session, sets language (`hi-IN`, `en-IN`), returns session_id + greeting |
| `POST` | `/api/v1/session/{id}/turn` | Takes audio binary or transcribed text. Returns agent voice response (TTS audio + text), updated slots, confirmation prompt |
| `POST` | `/api/v1/session/{id}/photo` | Accepts multipart image upload. Runs quality check (blur/exposure). Rejects if blurred (< 100 laplacian var), else stores |
| `POST` | `/api/v1/session/{id}/analyze` | Runs classifier -> reasoner -> policy layer. Saves prediction + brief. Returns final verdict |
| `GET` | `/api/v1/session/{id}/brief` | Returns structured 1-page JSON for clinician view |
| `POST` | `/api/v1/session/{id}/brief/review` | Clinician one-click approve / override sign-off |
| `POST` | `/api/v1/admin/mode` | Toggles system mode (`autonomous` ↔ `supervised`) |
| `GET` | `/api/v1/admin/mode` | Returns active policy mode and thresholds |

---

## 🧪 Agent Validation Checklist (Section 6)

All 5 directive test cases are verified in `tests/test_directive_checklist.py`:

- [x] **Test Case 1 (Scabies Catch)**: Input slots: `duration_days=14, has_itching=True, household_contacts_affected=True`. Reasoner elevates scabies into top-2 differential even if image model is uncertain.
- [x] **Test Case 2 (Malignancy Policy Red Flag)**: Classifier returns `possible_malignancy` with confidence 0.55. Policy returns `action="refer_only"`, `urgency="emergency"|"seek_opd"`, and never displays a reassuring message.
- [x] **Test Case 3 (Fever Red Flag)**: Input `has_fever=True`. Policy forces `always_refer` with reason `fever_with_rash`.
- [x] **Test Case 4 (Mode Switch Verification)**: Set `policy.yaml` to `supervised`. Confident case outputs `action="supervised_queue"` and message states *"Doctor will review"*. Switch to `autonomous`—outputs `action="speak_verdict"`.
- [x] **Test Case 5 (Negative Guardrails)**: Output never contains drug units (`mg`, `tablet`, `twice daily`) or medication names (`prednisone`, `amoxicillin`, etc.).

Run the checklist:
```powershell
python -u run_tests.py
# or
python -m pytest tests/test_directive_checklist.py -v
```

---

## 🚀 How to Run

### Run Complete Test Suite
```powershell
python -u run_tests.py
```

### Start Backend API & Mobile-First Web Client
```powershell
python -m uvicorn services.api.main:app --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000/`** in your browser.
