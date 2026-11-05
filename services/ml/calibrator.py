"""
Temperature Scaling Calibration Module for Q-Doc MVP.
Applies temperature scaling (p_i = e^{z_i/T} / sum_j e^{z_j/T})
to calibrate classification logits and prevent overconfident false positives.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, List

class TemperatureCalibrator(nn.Module):
    def __init__(self, temperature: float = 1.28):
        super().__init__()
        self.temperature = nn.Parameter(torch.ones(1) * temperature)

    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        """Scales logits by temperature T."""
        t = torch.clamp(self.temperature, min=0.1)
        return logits / t

    def calibrate_numpy(self, logits_np: np.ndarray) -> np.ndarray:
        t_val = float(self.temperature.item())
        scaled = logits_np / max(0.1, t_val)
        exp = np.exp(scaled - np.max(scaled))
        return exp / np.sum(exp)

    def set_temperature(self, new_temp: float) -> None:
        with torch.no_grad():
            self.temperature.copy_(torch.ones(1) * new_temp)

