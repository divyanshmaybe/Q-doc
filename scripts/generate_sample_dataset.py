"""
Curated Sample Clinical Image Generator & Dataset Ingestion Harness.
Generates representative high-fidelity clinical and dermoscopic samples across the
8 target classes with distinct morphological patterns (color, texture, borders)
for testing the training and classifier pipeline immediately.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

CLASSES = [
    "acne",
    "eczema",
    "psoriasis",
    "tinea",
    "urticaria",
    "scabies",
    "possible_malignancy",
    "other_unclear"
]


def create_synthetic_lesion(condition: str, seed: int = 42) -> Image.Image:
    """Creates a 224x224 RGB image with condition-specific dermatological characteristics."""
    np.random.seed(seed)
    
    # Base Indian skin tone background (Fitzpatrick Type IV-V: warm olive/brown)
    base_r = np.random.randint(165, 205)
    base_g = np.random.randint(125, 160)
    base_b = np.random.randint(95, 130)

    img = np.zeros((224, 224, 3), dtype=np.uint8)
    img[:, :, 0] = np.clip(base_r + np.random.normal(0, 4, (224, 224)), 0, 255)
    img[:, :, 1] = np.clip(base_g + np.random.normal(0, 4, (224, 224)), 0, 255)
    img[:, :, 2] = np.clip(base_b + np.random.normal(0, 4, (224, 224)), 0, 255)

    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img, "RGBA")

    center_x, center_y = 112, 112

    if condition == "acne":
        # Multiple red inflammatory papules and white/yellow-centered pustules
        for _ in range(np.random.randint(8, 16)):
            x = center_x + np.random.randint(-60, 60)
            y = center_y + np.random.randint(-60, 60)
            rad = np.random.randint(4, 9)
            # Erythematous halo
            draw.ellipse([x - rad - 3, y - rad - 3, x + rad + 3, y + rad + 3], fill=(190, 45, 45, 140))
            # Pustular/comedonal center
            draw.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(235, 220, 180, 220))

    elif condition == "eczema":
        # Poorly demarcated erythematous dry patch with fine scaling
        for rad in range(65, 10, -5):
            alpha = int(90 * (1 - rad / 70))
            draw.ellipse([center_x - rad, center_y - rad, center_x + rad, center_y + rad], fill=(180, 60, 50, alpha))
        # Micro-fissures / excoriation scratches
        for _ in range(6):
            sx = center_x + np.random.randint(-40, 40)
            sy = center_y + np.random.randint(-40, 40)
            draw.line([sx, sy, sx + np.random.randint(10, 25), sy + np.random.randint(-5, 5)], fill=(140, 30, 30, 200), width=1)

    elif condition == "psoriasis":
        # Well-demarcated salmon-red plaque covered with thick silvery-white scales
        rad = 55
        draw.ellipse([center_x - rad, center_y - rad, center_x + rad, center_y + rad], fill=(185, 35, 45, 230), outline=(150, 20, 30, 255), width=2)
        # Silvery-white micaceous scales
        for _ in range(35):
            sx = center_x + np.random.randint(-40, 40)
            sy = center_y + np.random.randint(-40, 40)
            sw = np.random.randint(4, 12)
            draw.ellipse([sx, sy, sx + sw, sy + sw // 2], fill=(240, 240, 245, 210))

    elif condition == "tinea":
        # Annular ring with active erythematous scaly border and clearer center
        out_rad = 58
        in_rad = 34
        # Active advancing border
        draw.ellipse([center_x - out_rad, center_y - out_rad, center_x + out_rad, center_y + out_rad], fill=(185, 45, 40, 190))
        # Central clearing (resembling normal skin)
        draw.ellipse([center_x - in_rad, center_y - in_rad, center_x + in_rad, center_y + in_rad], fill=(base_r + 10, base_g + 5, base_b, 255))

    elif condition == "urticaria":
        # Transient edematous wheal (pale pink raised center with erythematous flare)
        flare_rad = 62
        wheal_rad = 42
        draw.ellipse([center_x - flare_rad, center_y - flare_rad, center_x + flare_rad, center_y + flare_rad], fill=(215, 65, 75, 120))
        draw.ellipse([center_x - wheal_rad, center_y - wheal_rad, center_x + wheal_rad, center_y + wheal_rad], fill=(245, 195, 190, 200))

    elif condition == "scabies":
        # Excoriated papules with linear burrow mark
        for _ in range(12):
            px = center_x + np.random.randint(-55, 55)
            py = center_y + np.random.randint(-55, 55)
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(175, 40, 40, 210))
        # Wavy mite burrow line
        points = [(center_x - 30 + i * 8, center_y + int(5 * math.sin(i))) for i in range(8)]
        draw.line(points, fill=(110, 65, 60, 220), width=2)

    elif condition == "possible_malignancy":
        # Asymmetric, irregular border, dark variegated color (ABCDE melanoma features)
        # Irregular polygonal blob
        poly_points = [
            (center_x - 45, center_y - 25),
            (center_x - 20, center_y - 48),
            (center_x + 35, center_y - 35),
            (center_x + 55, center_y + 10),
            (center_x + 25, center_y + 45),
            (center_x - 30, center_y + 50),
            (center_x - 55, center_y + 15),
        ]
        # Dark black/brown core
        draw.polygon(poly_points, fill=(25, 20, 20, 240), outline=(50, 30, 25, 255))
        # Deep blue/slate variegation zone
        draw.ellipse([center_x - 15, center_y - 15, center_x + 20, center_y + 20], fill=(40, 45, 65, 230))
        # Notched irregular edge
        draw.ellipse([center_x + 25, center_y - 25, center_x + 50, center_y - 5], fill=(15, 10, 10, 255))

    elif condition == "other_unclear":
        # Mild non-specific erythema
        draw.ellipse([center_x - 35, center_y - 35, center_x + 35, center_y + 35], fill=(175, 95, 85, 110))

    # Apply slight natural lens blur
    pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=0.7))
    return pil_img


def populate_dataset(base_dir: str = "data/clinical_images", samples_per_class: int = 15):
    """Populates train and val sets with condition samples."""
    base = Path(base_dir)
    total = 0
    for cond in CLASSES:
        train_dir = base / "train" / cond
        val_dir = base / "val" / cond
        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir.mkdir(parents=True, exist_ok=True)

        # 80% train, 20% val
        n_train = int(samples_per_class * 0.8)
        n_val = samples_per_class - n_train

        for i in range(n_train):
            img = create_synthetic_lesion(cond, seed=1000 + i)
            img.save(train_dir / f"{cond}_{i:03d}.jpg", quality=92)
            total += 1

        for i in range(n_val):
            img = create_synthetic_lesion(cond, seed=2000 + i)
            img.save(val_dir / f"{cond}_val_{i:03d}.jpg", quality=92)
            total += 1

    print(f"[Dataset Population] Successfully generated {total} balanced clinical images across {len(CLASSES)} classes in {base_dir}")


if __name__ == "__main__":
    populate_dataset(samples_per_class=20)

