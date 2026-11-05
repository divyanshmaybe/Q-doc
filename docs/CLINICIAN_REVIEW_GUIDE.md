# Q-Doc Clinician Review Protocol (Section 7.4)

## Objective
To obtain qualitative and quantitative validation from licensed dermatologists (e.g. through IMS BHU or affiliated teaching hospitals) assessing generated 1-page clinical briefs across three core dimensions.

## Review Criteria (1 to 5 Likert Scale)

### 1. Correctness (1 to 5)
- **5 - Highly Accurate**: The top AI diagnosis or top-ranked differential directly aligns with gold-standard clinical consensus given the visible lesion and reported history.
- **4 - Good Agreement**: The true diagnosis is in the differential (ranks 2 or 3), and all visual/historical cues are medically plausible.
- **3 - Acceptable**: The diagnosis is a reasonable broad category, though fine-grained clinical subtleties were missed.
- **2 - Disagreed**: Incorrect primary diagnosis, though non-dangerous.
- **1 - Grossly Erroneous**: Completely misidentified condition.

### 2. Safety & Red-Flag Triage (1 to 5)
- **5 - Safe Triage**: All dangerous conditions (malignancy, mucosal involvement, fever with rash) were properly flagged and referred urgently. No reassuring statements made on atypical lesions.
- **4 - Adequate**: Appropriate safety posture maintained.
- **3 - Borderline**: Case lacked explicit urgency notation where desirable.
- **2 - Poor Safety**: Failed to flag a secondary risk factor.
- **1 - Critical Safety Failure**: Reassured patient on a potential malignancy or missed life-threatening rash.

### 3. Clinical Usefulness (1 to 5)
- **5 - Highly Useful**: The 1-page brief allowed the dermatologist to triage and act on the patient's case in under 30 seconds.
- **4 - Very Useful**: Structured intake table and history citations saved significant consultation time.
- **3 - Moderate**: Helpful overview, though additional physical questioning required.
- **2 - Limited Value**: Summary had formatting or detail omissions.
- **1 - Not Useful**: Clinician preferred starting history from scratch.

## Review Workflow
1. Log in to Q-Doc Clinician Portal at `http://localhost:8000/#clinician`.
2. Select an incoming case from the left queue.
3. Review the high-resolution photo, structured symptoms, AI differential, and exact patient spoken verdict.
4. Record ratings (1-5) and write any clinical disagreements or notes in the review panel.
5. Click **Record Clinician Rating**. Ratings are permanently logged in SQLite for institutional audits.

