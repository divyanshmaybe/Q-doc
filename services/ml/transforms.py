"""
Phone Photo Conditions Degradation Simulation Pipeline.
Simulates real-world mobile photography degradation for training robust clinical vision models:
1. Motion and Defocus Blur (camera shake, poor auto-focus)
2. Illumination & Color Temperature variations (fluorescent hospital light, tungsten indoor warm, shadow casting)
3. Sensor Noise (Poisson low-light grain, high ISO artifacts)
4. Mobile JPEG Compression degradation (Q=35-70)
5. Perspective & Angle distortion
"""

import io
import math
import random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import torchvision.transforms as T
import torch


class PhoneDegradationSimulator:
    """
    Applies stochastic phone camera degradation transforms to simulate
    diverse real-world clinical smartphone photography.
    """
    def __init__(
        self,
        blur_prob: float = 0.5,
        lighting_prob: float = 0.6,
        noise_prob: float = 0.4,
        compression_prob: float = 0.7,
        shadow_prob: float = 0.35
    ):
        self.blur_prob = blur_prob
        self.lighting_prob = lighting_prob
        self.noise_prob = noise_prob
        self.compression_prob = compression_prob
        self.shadow_prob = shadow_prob

    def simulate(self, image: Image.Image) -> Image.Image:
        """Applies full chain of stochastic degradation."""
        img = image.copy().convert("RGB")

        # 1. Lighting & Color Temperature Shifts
        if random.random() < self.lighting_prob:
            img = self._apply_illumination_shift(img)

        # 2. Defocus / Motion Blur
        if random.random() < self.blur_prob:
            img = self._apply_blur(img)

        # 3. Vignetting / Shadow Cast
        if random.random() < self.shadow_prob:
            img = self._apply_shadow_cast(img)

        # 4. Sensor Noise (High ISO in dark clinics)
        if random.random() < self.noise_prob:
            img = self._apply_sensor_noise(img)

        # 5. JPEG Mobile Compression
        if random.random() < self.compression_prob:
            img = self._apply_jpeg_compression(img)

        return img

    def _apply_illumination_shift(self, img: Image.Image) -> Image.Image:
        # Choose lighting environment: Tungsten (warm), Fluorescent (green/cool), Under-exposed
        shift_type = random.choice(["warm_tungsten", "cool_fluorescent", "underexposed", "harsh_flash"])
        arr = np.array(img, dtype=np.float32)

        if shift_type == "warm_tungsten":
            arr[:, :, 0] = np.clip(arr[:, :, 0] * random.uniform(1.08, 1.25), 0, 255)
            arr[:, :, 2] = np.clip(arr[:, :, 2] * random.uniform(0.75, 0.90), 0, 255)
        elif shift_type == "cool_fluorescent":
            arr[:, :, 0] = np.clip(arr[:, :, 0] * random.uniform(0.85, 0.95), 0, 255)
            arr[:, :, 1] = np.clip(arr[:, :, 1] * random.uniform(1.05, 1.15), 0, 255)
            arr[:, :, 2] = np.clip(arr[:, :, 2] * random.uniform(1.08, 1.20), 0, 255)
        elif shift_type == "underexposed":
            arr = np.clip(arr * random.uniform(0.55, 0.80), 0, 255)
        elif shift_type == "harsh_flash":
            # Central hot spot
            h, w = arr.shape[:2]
            y, x = np.ogrid[:h, :w]
            center_y, center_x = h / 2, w / 2
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_dist = math.sqrt(center_x**2 + center_y**2)
            flash_mask = np.clip(1.4 - 0.7 * (dist / max_dist), 0.7, 1.4)[:, :, np.newaxis]
            arr = np.clip(arr * flash_mask, 0, 255)

        return Image.fromarray(arr.astype(np.uint8))

    def _apply_blur(self, img: Image.Image) -> Image.Image:
        # Defocus Gaussian blur vs Linear motion blur
        if random.random() < 0.6:
            radius = random.uniform(0.8, 2.4)
            return img.filter(ImageFilter.GaussianBlur(radius=radius))
        else:
            # Simple motion streak
            arr = np.array(img, dtype=np.float32)
            ksize = random.choice([3, 5, 7])
            kernel = np.zeros((ksize, ksize))
            if random.random() < 0.5:
                kernel[int((ksize - 1) / 2), :] = np.ones(ksize)
            else:
                kernel[:, int((ksize - 1) / 2)] = np.ones(ksize)
            kernel /= ksize
            import scipy.ndimage as ndimage
            for c in range(3):
                arr[:, :, c] = ndimage.convolve(arr[:, :, c], kernel)
            return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    def _apply_shadow_cast(self, img: Image.Image) -> Image.Image:
        arr = np.array(img, dtype=np.float32)
        h, w = arr.shape[:2]
        # Diagonal shadow gradient (hand holding camera obstructing ambient light)
        grad = np.linspace(random.uniform(0.5, 0.75), 1.0, w)
        grad_2d = np.tile(grad, (h, 1))[:, :, np.newaxis]
        arr = np.clip(arr * grad_2d, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _apply_sensor_noise(self, img: Image.Image) -> Image.Image:
        arr = np.array(img, dtype=np.float32)
        sigma = random.uniform(4.0, 15.0)
        noise = np.random.normal(0, sigma, arr.shape)
        arr = np.clip(arr + noise, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _apply_jpeg_compression(self, img: Image.Image) -> Image.Image:
        quality = random.randint(35, 72)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        buf.seek(0)
        return Image.open(buf).convert("RGB")

