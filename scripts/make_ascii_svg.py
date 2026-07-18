"""
Convert prepped grayscale photo into a self-typing monochrome ASCII art SVG.

Key fixes:
- INVERTED ramp: dark pixels (face features) -> dense chars, bright pixels (background) -> spaces
- Proper aspect ratio handling for portrait photos
- Monochrome single-color for clean look
- CSS keyframe row-by-row reveal with cursor
"""
import numpy as np
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ASCII density ramp: sparse (bright/background) to dense (dark/features)
RAMP = " .':;-~=+*cs#%@"
COLS = 80
CHAR_W = 7.2
CHAR_H = 14
FG = "#c0c0c0"
BG = "#0d1117"
FONT = "'Courier New', Courier, monospace"
FONT_SIZE = 11
ROW_DELAY = 0.04   # stagger between rows
ROW_DUR = 0.12     # time for one row to reveal


def brightness_to_char(val):
    """Map pixel brightness (0=black, 255=white) to ASCII character.
    Dark pixels -> dense characters (end of ramp).
    Bright pixels -> sparse characters / space (start of ramp).
    """
    # Invert: 255 (white/bright) -> index 0 (space), 0 (black/dark) -> last index (dense)
    idx = int((1 - val / 255) * (len(RAMP) - 1))
    idx = max(0, min(len(RAMP) - 1, idx))
    return RAMP[idx]


def main():
    img = Image.open(str(ROOT / "data" / "source-prepped.png")).convert("L")
    w, h = img.size
    
    # Compute rows to maintain aspect ratio
    # ASCII chars are taller than wide, so adjust
    char_aspect = CHAR_W / CHAR_H  # ~0.51
    img_aspect = w / h
    ROWS = int(COLS / img_aspect * char_aspect)
    
    print(f"[ascii] Image {w}x{h}, grid {COLS}x{ROWS}, char_aspect={char_aspect:.2f}")
    
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    pixels = np.array(img)

    svg_w = COLS * CHAR_W + 20
    svg_h = ROWS * CHAR_H + 20

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    lines.append(f'<rect width="100%" height="100%" fill="{BG}"/>')
    lines.append('<style>')
    lines.append(f'  text {{ font-family: {FONT}; font-size: {FONT_SIZE}px; fill: {FG}; dominant-baseline: hanging; white-space: pre; }}')

    # CSS keyframes for each row wipe
    for r in range(ROWS):
        lines.append(f'  @keyframes rr{r} {{ 0% {{ clip-path: inset(0 100% 0 0); }} 100% {{ clip-path: inset(0 0% 0 0); }} }}')

    lines.append('</style>')

    # Render each row
    for r in range(ROWS):
        row_chars = ''.join(brightness_to_char(pixels[r, c]) for c in range(COLS))
        # XML-escape
        row_chars = row_chars.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        y = 10 + r * CHAR_H
        delay = r * ROW_DELAY
        lines.append(
            f'<text x="10" y="{y}" xml:space="preserve" '
            f'style="animation: rr{r} {ROW_DUR}s {delay:.3f}s linear forwards; clip-path: inset(0 100% 0 0);">'
            f'{row_chars}</text>'
        )

    # Cursor that moves down row-by-row then disappears
    cursor_ys = [str(10 + r * CHAR_H) for r in range(ROWS)]
    total_time = ROWS * ROW_DELAY + ROW_DUR
    lines.append(f'<rect x="10" width="7" height="{CHAR_H}" fill="{FG}" opacity="0.9">')
    lines.append(f'  <animate attributeName="y" values="{";".join(cursor_ys)}" dur="{total_time}s" fill="freeze"/>')
    lines.append(f'  <animate attributeName="opacity" values="0.9;0" begin="{total_time}s" dur="0.3s" fill="freeze"/>')
    lines.append('</rect>')

    lines.append('</svg>')

    out = ROOT / "afnaan-ascii.svg"
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f"[ascii] Written {out} ({COLS}x{ROWS} chars, {len(lines)} SVG lines)")


if __name__ == "__main__":
    main()
