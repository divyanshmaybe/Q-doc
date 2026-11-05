"""
Evaluation Metrics Calculator for Q-Doc MVP.
Computes Top-1/Top-3 accuracy, Wilson 95% confidence intervals,
Expected Calibration Error (ECE), Dangerous Class Recall,
and Stratified Accuracy by Fitzpatrick Skin Tone.
"""

import math
from typing import List, Dict, Any, Tuple
from collections import defaultdict

def wilson_score_interval(successes: int, total: int, z: float = 1.96) -> Tuple[float, float]:
    """Calculates Wilson 95% confidence interval for proportions."""
    if total == 0:
        return 0.0, 0.0
    p = successes / total
    denom = 1 + (z ** 2) / total
    center = (p + (z ** 2) / (2 * total)) / denom
    spread = (z / denom) * math.sqrt((p * (1 - p) / total) + (z ** 2) / (4 * (total ** 2)))
    return round(max(0.0, center - spread) * 100, 1), round(min(1.0, center + spread) * 100, 1)

def compute_expected_calibration_error(
    confidences: List[float],
    accuracies: List[bool],
    num_bins: int = 5
) -> Tuple[float, List[Dict[str, Any]]]:
    """Computes Expected Calibration Error (ECE) and reliability curve data."""
    bin_boundaries = [i / num_bins for i in range(num_bins + 1)]
    total_samples = len(confidences)
    if total_samples == 0:
        return 0.0, []

    ece = 0.0
    curve_data = []

    for i in range(num_bins):
        b_low = bin_boundaries[i]
        b_high = bin_boundaries[i + 1]

        # Samples falling into current confidence bin
        indices = [
            idx for idx, c in enumerate(confidences)
            if (b_low <= c < b_high) or (i == num_bins - 1 and c == b_high)
        ]
        bin_count = len(indices)
        if bin_count > 0:
            avg_conf = sum(confidences[idx] for idx in indices) / bin_count
            bin_acc = sum(1 for idx in indices if accuracies[idx]) / bin_count
            ece += (bin_count / total_samples) * abs(bin_acc - avg_conf)
            curve_data.append({
                "bin_name": f"{int(b_low*100)}-{int(b_high*100)}%",
                "avg_confidence": round(avg_conf * 100, 1),
                "accuracy": round(bin_acc * 100, 1),
                "count": bin_count
            })
        else:
            mid = (b_low + b_high) / 2
            curve_data.append({
                "bin_name": f"{int(b_low*100)}-{int(b_high*100)}%",
                "avg_confidence": round(mid * 100, 1),
                "accuracy": round(mid * 100, 1),
                "count": 0
            })

    return round(ece * 100, 2), curve_data

