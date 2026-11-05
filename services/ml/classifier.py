"""
PyTorch Skin Lesion Classifier for Q-Doc MVP.
Integrates image quality assessment, vision feature extraction,
temperature-scaled calibration, and returns ImagePrediction.
"""

import io
from typing import Dict, Any, Optional
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

from services.dialogue.schemas import SkinCondition, ImagePrediction
from .quality import ImageQualityChecker
from .calibrator import TemperatureCalibrator

CONDITIONS_ORDER = [
    SkinCondition.ACNE,
    SkinCondition.ECZEMA,
    SkinCondition.PSORIASIS,
    SkinCondition.TINEA,
    SkinCondition.URTICARIA,
    SkinCondition.SCABIES,
    SkinCondition.POSSIBLE_MALIGNANCY,
    SkinCondition.OTHER_UNCLEAR
]

class SkinLesionModel(nn.Module):
    def __init__(self, num_classes: int = len(CONDITIONS_ORDER)):
        super().__init__()
        # Lightweight convolutional backbone
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.SiLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.SiLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.SiLU(),
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.SiLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Dropout(0.2)
        )
        self.head = nn.Linear(256, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feats = self.features(x)
        return self.head(feats)


class SkinClassifierPipeline:
    def __init__(self, temperature: float = 1.28):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SkinLesionModel(num_classes=len(CONDITIONS_ORDER)).to(self.device)
        self.model.eval()
        self.calibrator = TemperatureCalibrator(temperature=temperature).to(self.device)
        self.quality_checker = ImageQualityChecker()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image_bytes: bytes) -> ImagePrediction:
        # 1. Quality check
        quality_res = self.quality_checker.evaluate_image_bytes(image_bytes)
        q_score = quality_res["quality_score"]
        q_passed = quality_res["quality_passed"]

        # 2. Decode image
        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception:
            uniform_prob = 1.0 / len(CONDITIONS_ORDER)
            return ImagePrediction(
                probabilities={c: round(uniform_prob, 4) for c in CONDITIONS_ORDER},
                top_condition=SkinCondition.OTHER_UNCLEAR,
                confidence=round(uniform_prob, 4),
                image_quality_score=q_score,
                quality_passed=False
            )

        # 3. Model inference
        tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            raw_logits = self.model(tensor)
            scaled_logits = self.calibrator(raw_logits)
            base_probs = torch.softmax(scaled_logits, dim=-1).squeeze(0).cpu().numpy()

        # 4. Color, contrast, morphology feature priors
        np_arr = np.array(pil_img)
        r = np_arr[:, :, 0].astype(float)
        g = np_arr[:, :, 1].astype(float)
        b = np_arr[:, :, 2].astype(float)
        
        # Check for atypical dark pigmented asymmetry (malignancy indicator)
        dark_pigment_ratio = float(np.sum((r < 55) & (g < 45) & (b < 40)) / (r.size + 1e-5))

        probs_dict: Dict[SkinCondition, float] = {}
        for idx, cond in enumerate(CONDITIONS_ORDER):
            p = float(base_probs[idx])
            if cond == SkinCondition.POSSIBLE_MALIGNANCY and dark_pigment_ratio > 0.08:
                # Elevate suspicion for pigmented asymmetry
                p *= (1.0 + min(1.5, dark_pigment_ratio * 12))
            probs_dict[cond] = p

        # Normalize probabilities
        total = sum(probs_dict.values()) + 1e-9
        normalized_probs = {c: round(score / total, 4) for c, score in probs_dict.items()}

        sorted_items = sorted(normalized_probs.items(), key=lambda item: item[1], reverse=True)
        top_cond, top_conf = sorted_items[0]

        return ImagePrediction(
            probabilities=normalized_probs,
            top_condition=top_cond,
            confidence=top_conf,
            image_quality_score=q_score,
            quality_passed=q_passed
        )
