# Q-Doc 3-Minute Pitch & Demo Script

Follow this precise sequence to demonstrate the Q-Doc MVP during investor pitches, academic evaluations, or clinical reviews.

---

## ⏱ Timeline Breakdown

### Minute 0:00 - 0:45 &bull; Step 1 & 2: Voice-Native Hindi Consultation
1. Open the Q-Doc web app at `http://localhost:8000/`.
2. Notice the Language Selector set to **हिंदी (Hindi)**.
3. Review the top informed consent banner stating:
   > *"स्क्रीनिंग सहायता (Screening Aid): यह AI सहायक केवल प्रारंभिक जांच के लिए है, डॉक्टर का विकल्प नहीं।"*
4. Tap the large pulsing **Microphone button** and speak naturally in Hindi:
   > *"मुझे दो हफ्ते से हाथों और कोहनी के जोड़ों पर बहुत तेज खुजली हो रही है और त्वचा लाल पड़ गई है।"*
5. Point out how the dialogue engine extracts key intake slots in real time:
   - **अंग (Body Site)**: Hands & elbow creases
   - **अवधि (Duration)**: 2 weeks
   - **खुजली (Itch)**: Intense itching
   - **बुखार (Fever)**: None reported
6. The agent performs a **Confirmation Turn** cheaply catching speech errors:
   > *"आपने बताया कि यह समस्या दो हफ्ते से हाथों और कोहनी पर है..."*
7. Tap **"हाँ, बिल्कुल सही है" (Yes, Correct)**.

---

### Minute 0:45 - 1:30 &bull; Step 3 & 4: Photo Capture, Quality Gate & Diagnosis
1. Tap **"तस्वीर खींचें या अपलोड करें"** to activate the camera or load an image.
2. Highlight the **Quality Analyzer**:
   - Laplacian Sharpness variance calculated in real-time.
   - Brightness / Luminance check ensuring proper exposure.
   - Quality badge turns **"✓ Quality Clear"** (rejecting blurry or underexposed submissions).
3. The model classifies the condition against the closed 8-condition list.
4. The system presents the diagnosis:
   - **एक्जिमा / Eczema (Atopic Dermatitis)** with ~88% calibrated confidence.
   - Spoken audio verdict delivered in Hindi.
   - Non-prescriptive self-care recommendations (gentle moisturizers, avoiding harsh soaps). Zero medication dosages outputted!

---

### Minute 1:30 - 2:05 &bull; Step 5: Controllable Autonomy Handover
1. Point to the Autonomy switch in the header.
2. Click **"Supervised"** mode with one click.
3. Run or trigger a screening case in Supervised mode.
4. Show that the patient is politely told:
   > *"Your voice history and photograph have been recorded. A dermatologist will review your case file."*
5. Switch to the **"Doctor Briefs"** tab:
   - Show the structured 1-page summary arriving in the queue.
   - Point out patient demographics, structured intake table, lesion photo, differential, and red-flag screening.
   - Show the 1-to-5 star rating widget where a clinician signs off on Correctness, Safety, and Clinical Usefulness.

---

### Minute 2:05 - 2:40 &bull; Step 6: Proving "Gain from Voice History" (Scabies Demo)
1. Go to the **3-Min Demo** tab and click **Run Case 2** (Scabies).
2. Explain the fundamental Q-Doc value proposition:
   - On photo alone, an excoriated papular rash on the wrists looks ambiguous between Eczema (46%) and Scabies (34%).
   - But when the patient speaks: *"Itching is unbearable at night, and my brother living in my room is scratching too..."*
   - The multimodal diagnosis reasoner integrates the history:
     - Scabies probability leaps to **91%** (+45% diagnostic gain!).
     - The system cites the patient's exact words as clinical evidence.
   - **Key Pitch Quote**: *"Skin appearance is only half the story; clinical history is the other half."*

---

### Minute 2:40 - 3:00 &bull; Step 7: Showing Failure & Safety Transparently
1. Click **Run Case 3** (Malignancy Red Flag) or **Run Case 4** (Blurry Photo Abstention).
2. Demonstrate how Q-Doc handles edge cases:
   - A suspicious dark pigmented lesion triggers the **`possible_malignancy`** red-flag rule:
     The system **always refers** urgently and **never reassures** on potential skin cancer.
   - An intentionally blurry photo triggers the **Quality Abstention** gate with clear retake instructions.
3. Conclude with the Evaluation tab:
   - Stratified accuracy across Fitzpatrick skin tones (Types I-VI).
   - 100% recall on dangerous classes with honest Wilson 95% confidence intervals.

