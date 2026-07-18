"""
Prep the Gemini-generated ASCII art image for SVG conversion.
- Auto-crop the CRT monitor frame/border
- Convert to high-contrast grayscale
- Save as data/source-prepped.png
"""
import sys
import numpy as np
from PIL import Image, ImageOps
import cv2
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def auto_crop(img_np, threshold=40, margin=5):
    """Crop out the dark CRT frame border."""
    # Find rows and cols that aren't mostly black
    row_means = img_np.mean(axis=1)
    col_means = img_np.mean(axis=0)

    row_mask = row_means > threshold
    col_mask = col_means > threshold

    rows = np.where(row_mask)[0]
    cols = np.where(col_mask)[0]

    if len(rows) == 0 or len(cols) == 0:
        return img_np

    top, bottom = max(0, rows[0] - margin), min(img_np.shape[0], rows[-1] + margin)
    left, right = max(0, cols[0] - margin), min(img_np.shape[1], cols[-1] + margin)

    return img_np[top:bottom, left:right]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "source-photo.png")
    print(f"[prep] Loading {src}")

    img = Image.open(src).convert("L")
    print(f"[prep] Original size: {img.size}")

    gray_np = np.array(img)

    # Auto-crop the CRT frame border
    cropped = auto_crop(gray_np, threshold=50, margin=2)
    print(f"[prep] After crop: {cropped.shape[1]}x{cropped.shape[0]}")

    # Apply CLAHE for strong local contrast
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(cropped)

    # Aggressive histogram stretch
    p_low, p_high = np.percentile(enhanced, (1, 99))
    enhanced = np.clip((enhanced.astype(float) - p_low) / (p_high - p_low) * 255, 0, 255).astype(np.uint8)

    print(f"[prep] Enhanced. Range: [{enhanced.min()}, {enhanced.max()}]")

    # Save
    out_path = ROOT / "data" / "source-prepped.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(enhanced).save(str(out_path))
    print(f"[prep] Saved to {out_path} ({enhanced.shape[1]}x{enhanced.shape[0]})")


if __name__ == "__main__":
    main()
