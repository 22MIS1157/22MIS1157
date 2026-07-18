import sys, io
import numpy as np
from PIL import Image
import cv2
from rembg import remove
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "source-photo.png")
    print(f"[prep] Loading {src}")
    
    # 1. Remove background
    with open(src, "rb") as f:
        raw = f.read()
    out_bytes = remove(raw)
    img = Image.open(io.BytesIO(out_bytes)).convert("RGBA")
    print(f"[prep] Background removed. Size: {img.size}")
    
    # 2. Composite onto white
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white, img)
    gray_pil = composited.convert("L")
    
    # 3. CLAHE contrast enhancement
    gray_np = np.array(gray_pil)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray_np)
    print(f"[prep] CLAHE applied.")
    
    # 4. Save
    out_path = ROOT / "data" / "source-prepped.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(enhanced).save(str(out_path))
    print(f"[prep] Saved to {out_path}")

if __name__ == "__main__":
    main()
