"""
Image Quality Pipeline for Q-Doc MVP.
Removes artificial blur barriers so real user skin captures (smooth rashes, lesions, webcams)
are never discarded. Flat zero-detail artifacts or unreadable files are cleanly caught.
"""

from typing import Dict, Any
import cv2
import numpy as np

class ImageQualityChecker:
    def __init__(
        self,
        blur_variance_threshold: float = 0.5,
        min_brightness: float = 15.0,
        max_brightness: float = 245.0
    ):
        # Threshold set to 0.5 so only flat zero-detail / artificial solids fail;
        # real skin textures (even smooth lesions with variance 5-30) pass seamlessly.
        self.blur_variance_threshold = blur_variance_threshold
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness

    def evaluate_image_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {
                "quality_score": 0.0,
                "quality_passed": False,
                "blur_score": 0.0,
                "brightness_score": 0.0,
                "reasons": ["Unreadable image format"],
                "guidance_hi": "फोटो लोड नहीं हो सकी। कृपया एक वैध फोटो अपलोड करें।",
                "guidance_en": "Failed to decode image file. Please provide a valid JPG or PNG."
            }
        return self.evaluate_cv2_image(img)

    def evaluate_cv2_image(self, img: np.ndarray) -> Dict[str, Any]:
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Laplacian variance for blur / texture analysis
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_variance = float(laplacian.var())

        # Blur barrier removed: Real dermatological captures (smooth skin, rashes, lesions)
        # naturally have low edge gradients. Any image with non-zero variation (variance > 0.5)
        # is accepted without blur penalty.
        is_blurred = blur_variance <= self.blur_variance_threshold

        if is_blurred:
            blur_norm = 0.0
        else:
            # Generous sharpness normalization for real skin photography
            blur_norm = min(1.0, 0.80 + (blur_variance / 50.0) * 0.20)

        # 2. Histogram / luminance analysis for exposure
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        total_pixels = float(h * w)
        dark_ratio = float(np.sum(hist[:15]) / total_pixels)
        bright_ratio = float(np.sum(hist[245:]) / total_pixels)
        mean_brightness = float(np.mean(gray))

        if mean_brightness < self.min_brightness or dark_ratio > 0.85:
            brightness_issue = "underexposed"
            bright_norm = max(0.0, mean_brightness / self.min_brightness)
        elif mean_brightness > self.max_brightness or bright_ratio > 0.80:
            brightness_issue = "overexposed"
            bright_norm = max(0.0, 1.0 - ((mean_brightness - self.max_brightness) / (255.0 - self.max_brightness)))
        else:
            brightness_issue = "good"
            bright_norm = 1.0

        # Composite quality score [0.0 to 1.0]
        # Real captures will comfortably sit at 0.85 - 0.98
        quality_score = round(float(0.60 * blur_norm + 0.40 * bright_norm), 3)

        reasons = []
        if is_blurred:
            reasons.append("blurry_image")
        if brightness_issue != "good":
            reasons.append(brightness_issue)

        # Quality pass condition:
        # Pass all valid photos. Only reject zero-variance flat blocks or extreme unreadable frames.
        quality_passed = (not is_blurred) and (quality_score >= 0.50)

        if is_blurred:
            guidance_hi = "कैमरा स्थिर रखें और फोकस करने के लिए स्क्रीन पर टैप करें।"
            guidance_en = "Hold the camera steady and tap to focus to avoid blur."
        elif brightness_issue == "underexposed":
            guidance_hi = "फोटो बहुत अंधेरी है। कृपया बेहतर रोशनी में दोबारा फोटो लें।"
            guidance_en = "The photo is too dark. Please take photo under adequate lighting."
        elif brightness_issue == "overexposed":
            guidance_hi = "फोटो पर बहुत तेज चमक है। फ्लैश से थोड़ा दूर हटकर फोटो लें।"
            guidance_en = "Too much direct glare. Please diffuse lighting and retake."
        else:
            guidance_hi = "फोटो की गुणवत्ता अच्छी और स्पष्ट है।"
            guidance_en = "Image quality is clear with good focus and illumination."

        return {
            "quality_score": quality_score,
            "quality_passed": quality_passed,
            "blur_score": round(blur_variance, 1),
            "brightness_score": round(mean_brightness, 1),
            "reasons": reasons,
            "guidance_hi": guidance_hi,
            "guidance_en": guidance_en
        }
