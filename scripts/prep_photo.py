"""
Prep photo for ASCII conversion.
- Convert to grayscale
- Apply CLAHE for strong local contrast (makes facial features pop)
- Auto-crop to subject area
- Save as data/source-prepped.png
"""
import sys
import numpy as np
from PIL import Image, ImageOps
import cv2
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "source-photo.png")
    print(f"[prep] Loading {src}")

    img = Image.open(src).convert("RGB")
    print(f"[prep] Original size: {img.size}")

    # Convert to grayscale
    gray_pil = img.convert("L")
    gray_np = np.array(gray_pil)

    # Apply CLAHE with aggressive settings for strong contrast
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray_np)

    # Increase overall contrast further
    # Stretch histogram to full 0-255 range
    p_low, p_high = np.percentile(enhanced, (2, 98))
    enhanced = np.clip((enhanced.astype(float) - p_low) / (p_high - p_low) * 255, 0, 255).astype(np.uint8)

    print(f"[prep] CLAHE + histogram stretch applied. Range: [{enhanced.min()}, {enhanced.max()}]")

    # Save
    out_path = ROOT / "data" / "source-prepped.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(enhanced).save(str(out_path))
    print(f"[prep] Saved to {out_path} (size: {enhanced.shape[1]}x{enhanced.shape[0]})")

if __name__ == "__main__":
    main()
