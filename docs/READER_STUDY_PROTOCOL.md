# Dermatologist Reader Study Protocol & Analysis Plan
**Document Version:** 1.0 (Track B Pre-Registered Protocol)  
**Status:** Pre-Registered (Locked Before Trial Execution)

---

## 1. Study Objective
To evaluate the diagnostic accuracy, sensitivity, specificity, and demographic equity of the **Q-Doc Multimodal AI Diagnostic Assistant** against a cohort of certified board-eligible/certified dermatologists on a frozen, blinded set of patient presentations.

---

## 2. Study Design & Blinding
- **Cohort Size:** 120 adjudicated clinical cases spanning all 8 target classes with equal distribution across Fitzpatrick Phototypes (Types I–III: 50%, Types IV–VI: 50%).
- **Readers:**
  - $N=3$ Certified Dermatologists ($R_1, R_2, R_3$) reviewing cases independently without access to AI predictions.
  - $N=1$ Senior Referee Dermatologist ($R_{\text{ref}}$) for resolving disagreements.
- **AI System:**
  - Q-Doc Multimodal Pipeline (frozen model checkpoint, temperature-calibrated).
- **Blinding Protocol:**
  - Both human readers and the AI receive the exact same inputs: (1) Standardized clinical phone photograph, (2) Normalized patient history transcript (site, duration, itch, fever, family clustering).

---

## 3. Pre-Registered Hypotheses & Success Thresholds
The following criteria were fixed **prior to evaluating test set results**:

1. **Non-Inferiority in Top-1 Accuracy:**
   $$\text{Accuracy}_{\text{AI}} \ge \text{Mean}(\text{Accuracy}_{\text{Dermatologists}}) - 5.0\%$$
2. **Dangerous Lesion Sensitivity (Zero-Tolerance Safety Gate):**
   $$\text{Sensitivity}_{\text{AI}}(\text{Melanoma / Malignancy}) \ge 95.0\% \quad (\text{with lower 95\% CI} \ge 85.0\%)$$
3. **Fitzpatrick Demographic Parity:**
   $$|\text{Accuracy}_{\text{Types I-III}} - \text{Accuracy}_{\text{Types IV-VI}}| \le 6.0\%$$
4. **Expected Calibration Error (ECE):**
   $$\text{ECE} \le 0.10$$

---

## 4. Primary & Secondary Statistical Endpoints
* **Primary:** Top-1 Concordance with Ground Truth.
* **Secondary:**
  * Top-3 Differential Concordance.
  * Per-Condition Sensitivity & Specificity with 95% Wilson Score Confidence Intervals.
  * Inter-Rater Agreement: Cohen's $\kappa$ between Dermatologist 1 and Dermatologist 2; Fleiss' $\kappa$ across all readers.
  * Gain from Voice History: $\Delta = \text{Accuracy}_{\text{Multimodal}} - \text{Accuracy}_{\text{Image-Only}}$.

---

## 5. Statistical Formulae & Confidence Intervals
Wilson score interval for binomial proportion $p$ with sample size $n$ at confidence level $Z_{1-\alpha/2} = 1.96$:
$$CI_{95} = \frac{p + \frac{Z^2}{2n} \pm Z \sqrt{\frac{p(1-p)}{n} + \frac{Z^2}{4n^2}}}{1 + \frac{Z^2}{n}}$$

