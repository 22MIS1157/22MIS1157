import numpy as np
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RAMP = ' .`:-=+*cs#%@'
COLS, ROWS = 90, 48
CHAR_W, CHAR_H = 7.2, 13
FG = "#c0c0c0"
BG = "#0d1117"
FONT = "monospace"
FONT_SIZE = 12
ROW_DELAY = 0.04
ROW_DUR = 0.15

def brightness_to_char(val):
    idx = int(val / 255 * (len(RAMP) - 1))
    return RAMP[idx]

def main():
    img = Image.open(str(ROOT / "data" / "source-prepped.png")).convert("L")
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    pixels = np.array(img)
    
    svg_w = COLS * CHAR_W + 20
    svg_h = ROWS * CHAR_H + 20
    
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    lines.append(f'<rect width="100%" height="100%" fill="{BG}"/>')
    lines.append(f'<style>')
    lines.append(f'  text {{ font-family: {FONT}; font-size: {FONT_SIZE}px; fill: {FG}; dominant-baseline: hanging; }}')
    
    for r in range(ROWS):
        lines.append(f'  @keyframes reveal-row-{r} {{')
        lines.append(f'    0% {{ clip-path: inset(0 100% 0 0); }}')
        lines.append(f'    100% {{ clip-path: inset(0 0% 0 0); }}')
        lines.append(f'  }}')
    
    lines.append(f'  @keyframes blink {{ 0%,49% {{ opacity:1 }} 50%,100% {{ opacity:0 }} }}')
    lines.append(f'</style>')
    
    for r in range(ROWS):
        row_chars = ''.join(brightness_to_char(pixels[r, c]) for c in range(COLS))
        row_chars = row_chars.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        y = 10 + r * CHAR_H
        delay = r * ROW_DELAY
        lines.append(f'<text x="10" y="{y}" style="animation: reveal-row-{r} {ROW_DUR}s {delay}s linear forwards; clip-path: inset(0 100% 0 0);">{row_chars}</text>')
    
    cursor_lines = []
    for r in range(ROWS):
        cursor_lines.append(f'{10 + r * CHAR_H}')
    
    total_time = ROWS * ROW_DELAY + ROW_DUR
    lines.append(f'<rect x="10" width="8" height="{CHAR_H}" fill="{FG}" opacity="0.8">')
    lines.append(f'  <animate attributeName="y" values="{";".join(cursor_lines)}" dur="{total_time}s" fill="freeze"/>')
    lines.append(f'  <animate attributeName="opacity" values="0.8;0" begin="{total_time}s" dur="0.3s" fill="freeze"/>')
    lines.append(f'</rect>')
    
    lines.append('</svg>')
    
    out = ROOT / "afnaan-ascii.svg"
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f"[ascii] Written {out} ({COLS}x{ROWS} chars)")

if __name__ == "__main__":
    main()
