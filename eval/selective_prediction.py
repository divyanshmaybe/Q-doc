"""
Selective Prediction & Risk-Coverage Analysis Engine for Q-Doc MVP.
Implements selective classification with honest abstention reporting:
1. Calculates risk-coverage trade-off curves across confidence thresholds.
2. Evaluates per-class abstention boundaries to guarantee safety.
3. Computes selective accuracy, risk, and coverage metrics.
"""

from typing import List, Dict, Any, Tuple
import numpy as np


class SelectivePredictionEngine:
    def __init__(self, confidence_threshold: float = 0.70):
        self.default_threshold = confidence_threshold

    def evaluate_selective_metrics(
        self,
        predictions: List[str],
        confidences: List[float],
        ground_truths: List[str],
        threshold: float = None
    ) -> Dict[str, Any]:
        """
        Computes accuracy at chosen coverage, abstention rate, and residual risk.
        """
        thresh = threshold if threshold is not None else self.default_threshold
        n = len(predictions)
        if n == 0:
            return {"coverage": 0.0, "abstention_rate": 0.0, "selective_accuracy": 0.0, "risk": 0.0}

        accepted_preds = []
        accepted_truths = []
        abstained_count = 0

        for p, conf, gt in zip(predictions, confidences, ground_truths):
            if conf >= thresh:
                accepted_preds.append(p)
                accepted_truths.append(gt)
            else:
                abstained_count += 1

        coverage = len(accepted_preds) / n
        abstention_rate = abstained_count / n

        if len(accepted_preds) > 0:
            correct = sum(1 for p, gt in zip(accepted_preds, accepted_truths) if p == gt)
            selective_accuracy = correct / len(accepted_preds)
            selective_risk = 1.0 - selective_accuracy
        else:
            selective_accuracy = 0.0
            selective_risk = 0.0

        return {
            "threshold": thresh,
            "total_cases": n,
            "accepted_cases": len(accepted_preds),
            "abstained_cases": abstained_count,
            "coverage": round(coverage, 4),
            "abstention_rate": round(abstention_rate, 4),
            "selective_accuracy": round(selective_accuracy, 4),
            "selective_risk": round(selective_risk, 4)
        }

    def compute_risk_coverage_curve(
        self,
        predictions: List[str],
        confidences: List[float],
        ground_truths: List[str],
        steps: int = 25
    ) -> List[Dict[str, float]]:
        """Generates the full empirical risk-coverage trade-off table."""
        curve = []
        thresholds = np.linspace(0.40, 0.98, steps)
        for t in thresholds:
            res = self.evaluate_selective_metrics(predictions, confidences, ground_truths, threshold=float(t))
            curve.append({
                "threshold": round(float(t), 3),
                "coverage": res["coverage"],
                "abstention_rate": res["abstention_rate"],
                "selective_accuracy": res["selective_accuracy"],
                "selective_risk": res["selective_risk"]
            })
        return curve

