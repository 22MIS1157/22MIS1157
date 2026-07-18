"""
Convert the prepped Gemini ASCII art image into a self-typing monochrome SVG.

Since the source is already a halftone/dot-pattern image with extreme contrast,
we use a wide character grid (120+ cols) and a refined density ramp for maximum
fidelity. The result should look very close to the Gemini original.

Animation: each row wipes left-to-right with staggered timing + a cursor block.
Plays once and freezes (no looping).
"""
import numpy as np
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Fine-grained density ramp (16 levels) - bright to dark
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

COLS = 120
CHAR_W = 6.6
CHAR_H = 12
FG = "#b0b8c0"          # cool gray on dark background
BG = "#0d1117"           # GitHub dark
FONT = "'Courier New', Courier, monospace"
FONT_SIZE = 10
ROW_DELAY = 0.03         # seconds between each row start
ROW_DUR = 0.08           # seconds for each row to fully reveal


def brightness_to_char(val):
    """Map pixel brightness (0=black, 255=white) to ASCII char.
    Dark pixels -> dense characters (end of ramp).
    Bright pixels -> sparse characters / space (start of ramp).
    """
    idx = int((1.0 - val / 255.0) * (len(RAMP) - 1))
    return RAMP[max(0, min(len(RAMP) - 1, idx))]


def main():
    img = Image.open(str(ROOT / "data" / "source-prepped.png")).convert("L")
    w, h = img.size

    # Compute rows to maintain aspect ratio
    char_aspect = CHAR_W / CHAR_H
    img_aspect = w / h
    ROWS = int(COLS / img_aspect * char_aspect)

    print(f"[ascii] Image {w}x{h}, grid {COLS}x{ROWS}")

    img = img.resize((COLS, ROWS), Image.LANCZOS)
    pixels = np.array(img)

    svg_w = COLS * CHAR_W + 20
    svg_h = ROWS * CHAR_H + 20

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    lines.append(f'<rect width="100%" height="100%" fill="{BG}"/>')
    lines.append('<style>')
    lines.append(f'  text {{ font-family: {FONT}; font-size: {FONT_SIZE}px; fill: {FG}; dominant-baseline: hanging; white-space: pre; }}')

    # One keyframe rule per row
    for r in range(ROWS):
        lines.append(f'  @keyframes rr{r} {{ 0% {{ clip-path: inset(0 100% 0 0); }} 100% {{ clip-path: inset(0 0% 0 0); }} }}')

    lines.append('</style>')

    # Render each row as a <text> element with clip animation
    for r in range(ROWS):
        row_chars = ''.join(brightness_to_char(pixels[r, c]) for c in range(COLS))
        # XML-escape special characters
        row_chars = (row_chars
                     .replace('&', '&amp;')
                     .replace('<', '&lt;')
                     .replace('>', '&gt;')
                     .replace('"', '&quot;')
                     .replace("'", '&apos;'))
        y = 10 + r * CHAR_H
        delay = r * ROW_DELAY
        lines.append(
            f'<text x="10" y="{y}" xml:space="preserve" '
            f'style="animation: rr{r} {ROW_DUR}s {delay:.3f}s linear forwards; '
            f'clip-path: inset(0 100% 0 0);">{row_chars}</text>'
        )

    # Animated cursor that moves down row-by-row
    cursor_ys = [str(10 + r * CHAR_H) for r in range(ROWS)]
    total_time = ROWS * ROW_DELAY + ROW_DUR
    lines.append(f'<rect x="10" width="6" height="{CHAR_H}" fill="{FG}" opacity="0.85">')
    lines.append(f'  <animate attributeName="y" values="{";".join(cursor_ys)}" dur="{total_time}s" fill="freeze"/>')
    lines.append(f'  <animate attributeName="opacity" values="0.85;0" begin="{total_time}s" dur="0.3s" fill="freeze"/>')
    lines.append('</rect>')

    lines.append('</svg>')

    out = ROOT / "afnaan-ascii.svg"
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f"[ascii] Written {out} ({COLS}x{ROWS} chars, {len(lines)} SVG lines)")


if __name__ == "__main__":
    main()
