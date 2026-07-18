"""
Embed the Gemini-generated ASCII art image directly into an SVG
with a top-to-bottom scanline reveal animation.

Instead of converting pixels to characters (which destroys quality),
this embeds the raster image as base64 inside the SVG and uses a
CSS clip-path animation to reveal it progressively from top to bottom,
simulating a CRT/terminal printing effect.

A glowing green scanline rides the reveal edge for extra effect.
"""
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BG = "#0d1117"
SCANLINE_COLOR = "#39d353"  # GitHub green
ANIM_DURATION = 2.5  # seconds for full reveal


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "source-photo.png")
    print(f"[ascii] Loading {src}")

    # Read image and base64 encode it
    with open(src, "rb") as f:
        img_bytes = f.read()
    b64 = base64.b64encode(img_bytes).decode("ascii")

    # Get image dimensions
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(img_bytes))
    img_w, img_h = img.size
    print(f"[ascii] Image size: {img_w}x{img_h}")

    # SVG dimensions with padding
    pad = 16
    svg_w = img_w + pad * 2
    svg_h = img_h + pad * 2

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'xmlns:xlink="http://www.w3.org/1999/xlink" '
               f'viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')

    # Dark background
    svg.append(f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>')

    # Styles and animations
    svg.append('<style>')
    svg.append(f'''
    @keyframes reveal {{
        0%   {{ clip-path: inset(0 0 100% 0); }}
        100% {{ clip-path: inset(0 0 0% 0); }}
    }}
    @keyframes scanline-move {{
        0%   {{ transform: translateY(0px); opacity: 1; }}
        95%  {{ transform: translateY({img_h}px); opacity: 1; }}
        100% {{ transform: translateY({img_h}px); opacity: 0; }}
    }}
    @keyframes glow-pulse {{
        0%, 100% {{ opacity: 0.4; }}
        50%      {{ opacity: 0.8; }}
    }}
    .ascii-img {{
        animation: reveal {ANIM_DURATION}s linear forwards;
        clip-path: inset(0 0 100% 0);
    }}
    .scanline {{
        animation: scanline-move {ANIM_DURATION}s linear forwards;
    }}
    .scanline-glow {{
        animation: scanline-move {ANIM_DURATION}s linear forwards,
                   glow-pulse 0.15s ease-in-out infinite;
    }}
    ''')
    svg.append('</style>')

    # Embedded image with reveal animation
    svg.append(f'<image class="ascii-img" x="{pad}" y="{pad}" '
               f'width="{img_w}" height="{img_h}" '
               f'href="data:image/png;base64,{b64}" '
               f'preserveAspectRatio="xMidYMid meet"/>')

    # Scanline effect (thin bright line that rides the reveal edge)
    svg.append(f'<g class="scanline" transform="translate(0, {pad})">')
    # Main scanline
    svg.append(f'  <rect x="{pad}" y="0" width="{img_w}" height="2" '
               f'fill="{SCANLINE_COLOR}" opacity="0.9"/>')
    # Glow behind scanline
    svg.append(f'  <rect class="scanline-glow" x="{pad}" y="-3" '
               f'width="{img_w}" height="8" fill="{SCANLINE_COLOR}" '
               f'opacity="0.3" filter="url(#blur)"/>')
    svg.append('</g>')

    # Blur filter for the glow
    svg.append('<defs>')
    svg.append('  <filter id="blur"><feGaussianBlur stdDeviation="3"/></filter>')
    svg.append('</defs>')

    # Subtle border
    svg.append(f'<rect width="100%" height="100%" rx="8" fill="none" '
               f'stroke="#30363d" stroke-width="1"/>')

    svg.append('</svg>')

    out = ROOT / "afnaan-ascii.svg"
    out.write_text('\n'.join(svg), encoding='utf-8')
    print(f"[ascii] Written {out} ({len(svg)} SVG lines, ~{len(b64)//1024}KB base64)")


if __name__ == "__main__":
    main()
