"""
Advanced Banner Generator with Logo Morphing Animation.
Morphs between:
  Phase 0: Afnaan's Floyd-Steinberg Dot Portrait (3.0s)
  Phase 1: Akatsuki Cloud Logo (2.0s)
  Phase 2: One Piece Strawhat Jolly Roger (2.0s)
  Phase 3: Deadpool Logo (2.0s)
Total loop duration: 14.2s with 1.3s smooth SMIL transitions.
"""
import os
import random
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
try:
    from rembg import remove
except ImportError:
    remove = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAIN_USER = r"C:\Users\Affu\.gemini\antigravity\brain\226fb60e-33bd-4628-ac5d-b326ef3d2cfb\.user_uploaded"

PHOTO_PATH = os.path.join(BRAIN_USER, "media__1785331609638.jpg")
AKATSUKI_PATH = os.path.join(BRAIN_USER, "media__1785333167781.png")
ONEPIECE_PATH = os.path.join(BRAIN_USER, "media__1785333221287.png")
DEADPOOL_PATH = os.path.join(BRAIN_USER, "media__1785333264837.png")

GRID_W = 280
GRID_H = 320

def floyd_steinberg_dither(img):
    pixels = img.load()
    w, h = img.size
    result = [[0 for _ in range(w)] for _ in range(h)]
    
    for y in range(h):
        serpentine = (y % 2 == 1)
        start_x = w - 1 if serpentine else 0
        end_x = -1 if serpentine else w
        step = -1 if serpentine else 1
        
        for x in range(start_x, end_x, step):
            oldpixel = pixels[x, y]
            newpixel = 255 if oldpixel > 127 else 0
            pixels[x, y] = newpixel
            result[y][x] = 1 if newpixel == 0 else 0
            
            quant_error = oldpixel - newpixel
            
            def add_error(nx, ny, factor):
                if 0 <= nx < w and 0 <= ny < h:
                    pixels[nx, ny] = min(max(int(pixels[nx, ny] + quant_error * factor), 0), 255)
            
            if not serpentine:
                add_error(x + 1, y, 7/16.0)
                add_error(x - 1, y + 1, 3/16.0)
                add_error(x, y + 1, 5/16.0)
                add_error(x + 1, y + 1, 1/16.0)
            else:
                add_error(x - 1, y, 7/16.0)
                add_error(x + 1, y + 1, 3/16.0)
                add_error(x, y + 1, 5/16.0)
                add_error(x - 1, y + 1, 1/16.0)
                
    return result

def extract_logo_points(img_path, num_points=700, target_w=280, target_h=320):
    img = Image.open(img_path).convert("RGBA")
    
    # Scale & fit inside target_w x target_h with padding
    w, h = img.size
    aspect = w / h
    if aspect > (target_w / target_h):
        nw = target_w - 20
        nh = int(nw / aspect)
    else:
        nh = target_h - 20
        nw = int(nh * aspect)
        
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    
    # Create canvas
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    px = (target_w - nw) // 2
    py = (target_h - nh) // 2
    canvas.paste(img, (px, py), img)
    
    # Extract non-transparent / dark pixels as candidate points
    arr = np.array(canvas)
    points = []
    
    # Alpha > 50 and luminance < 200 (for logo shapes)
    for y in range(target_h):
        for x in range(target_w):
            r, g, b, a = arr[y, x]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if a > 50 and lum < 220:
                points.append((x, y))
                
    if len(points) == 0:
        # Fallback to center grid
        points = [(target_w//2, target_h//2)]
        
    # Sample randomly or uniformly to get exactly num_points
    rnd = random.Random(42)
    if len(points) > num_points:
        points = rnd.sample(points, num_points)
    else:
        # Repeat points to match count
        while len(points) < num_points:
            p = rnd.choice(points)
            points.append((p[0] + rnd.randint(-1, 1), p[1] + rnd.randint(-1, 1)))
            
    return points

def process_portrait(img_path, is_dark):
    img = Image.open(img_path).convert("RGBA")
    if is_dark and remove is not None:
        try:
            img = remove(img)
        except Exception:
            pass
            
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, (0, 0), img)
    img = bg.convert("L")
    
    # Crop to 280x320
    w, h = img.size
    target_ratio = 280 / 320.0
    img_ratio = w / h
    if img_ratio > target_ratio:
        new_w = int(h * target_ratio)
        offset = (w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, h))
    else:
        new_h = int(w / target_ratio)
        offset = (h - new_h) // 2
        img = img.crop((0, offset, w, offset + new_h))
        
    img = img.resize((280, 320), Image.Resampling.LANCZOS)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    
    if is_dark:
        img = ImageOps.invert(img)
        
    return floyd_steinberg_dither(img)

def generate_svg(dot_matrix, logo1_pts, logo2_pts, logo3_pts, palette, is_dark, output_path):
    bg_color = palette['Background']
    chrome_color = palette['UI chrome']
    dot_color = palette['Portrait dots']
    text_color = palette['Text']
    accent_color = palette['Accent']
    
    num_groups = 60
    h = len(dot_matrix)
    w = len(dot_matrix[0])
    
    # Group portrait runs
    paths_by_group = {i: [] for i in range(num_groups)}
    rnd = random.Random(1337)
    
    for y in range(h):
        run_start = -1
        for x in range(w):
            if dot_matrix[y][x] == 1:
                if run_start == -1:
                    run_start = x
            else:
                if run_start != -1:
                    g = rnd.randint(0, num_groups - 1)
                    paths_by_group[g].append(f"M{run_start},{y}h{x - run_start}")
                    run_start = -1
        if run_start != -1:
            g = rnd.randint(0, num_groups - 1)
            paths_by_group[g].append(f"M{run_start},{y}h{w - run_start}")
            
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610" style="background-color: {bg_color}; font-family: monospace;">')
    
    # CSS Styles & SMIL
    svg.append('<style>')
    svg.append(f'.portrait-group {{ stroke: {dot_color}; stroke-width: 1; shape-rendering: crispEdges; opacity: 0; animation: introFade 0.5s forwards, loopPortrait 14.2s 2.0s infinite; }}')
    svg.append('@keyframes introFade { from { opacity: 0; } to { opacity: 1; } }')
    svg.append('@keyframes loopPortrait { 0% { opacity: 1; } 21.1% { opacity: 1; } 30.2% { opacity: 0; } 90.8% { opacity: 0; } 100% { opacity: 1; } }')
    
    for i in range(num_groups):
        delay = (i / num_groups) * 1.5
        svg.append(f'.g{i} {{ animation-delay: {delay:.2f}s, {2.0 + delay:.2f}s; }}')
        
    svg.append('.pulse { animation: p 2s infinite; }')
    svg.append('@keyframes p { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }')
    svg.append(f'.traveller {{ fill: {dot_color}; opacity: 0; animation: loopTraveller 14.2s 2.0s infinite; }}')
    svg.append('@keyframes loopTraveller { 0%, 21.1% { opacity: 0; } 30.2%, 90.8% { opacity: 0.9; } 100% { opacity: 0; } }')
    svg.append('</style>')
    
    # Outer Terminal Frame
    svg.append(f'<rect x="10" y="10" width="1160" height="590" fill="none" stroke="{chrome_color}" stroke-width="2"/>')
    svg.append(f'<rect x="10" y="10" width="1160" height="30" fill="{chrome_color}" opacity="0.1"/>')
    svg.append(f'<text x="25" y="30" fill="{chrome_color}" font-size="14" font-weight="bold">profile.sh --live</text>')
    
    # Handle pill badge top-right inside titlebar
    svg.append(f'<g transform="translate(960, 13)">')
    svg.append(f'<rect x="0" y="0" width="180" height="24" rx="12" fill="{accent_color}" opacity="0.9"/>')
    svg.append(f'<text x="90" y="16" fill="white" font-size="14" text-anchor="middle" font-weight="bold">@22MIS1157</text>')
    svg.append(f'</g>')
    
    # Portrait Container
    svg.append(f'<rect x="40" y="60" width="340" height="380" fill="none" stroke="{chrome_color}" stroke-width="1" opacity="0.5"/>')
    svg.append(f'<text x="40" y="460" fill="{chrome_color}" font-size="12">VISUAL.MAP</text>')
    
    # Label underneath visual map describing morphing phase
    svg.append(f'<text x="210" y="460" fill="{text_color}" font-size="11" text-anchor="middle" opacity="0.7">Morphing: Portrait ➔ Akatsuki ➔ One Piece ➔ Deadpool</text>')
    
    # Render Portrait Group (Layer 1)
    svg.append('<g transform="translate(70, 90)">')
    for i in range(num_groups):
        if paths_by_group[i]:
            path_data = " ".join(paths_by_group[i])
            svg.append(f'<path class="portrait-group g{i}" d="{path_data}"/>')
            
    # Render Traveller Dots (Layer 2 - Morphing between 3 logos)
    # KeyTimes in SMIL (total 14.2s):
    # t=0s: Portrait (hidden)
    # t=3.0s (0.211): Start morphing to Logo 1 (Akatsuki)
    # t=4.3s (0.302): Fully Logo 1 (Akatsuki)
    # t=6.3s (0.443): Hold Logo 1
    # t=7.6s (0.535): Fully Logo 2 (One Piece)
    # t=9.6s (0.676): Hold Logo 2
    # t=10.9s (0.767): Fully Logo 3 (Deadpool)
    # t=12.9s (0.908): Hold Logo 3 -> Return to Portrait
    # t=14.2s (1.000): Portrait
    
    num_travellers = min(len(logo1_pts), len(logo2_pts), len(logo3_pts))
    keytimes_str = "0; 0.211; 0.302; 0.443; 0.535; 0.676; 0.767; 0.908; 1"
    
    for idx in range(num_travellers):
        p1 = logo1_pts[idx]
        p2 = logo2_pts[idx]
        p3 = logo3_pts[idx]
        
        # Initial pos (Logo 1)
        cx1, cy1 = p1
        cx2, cy2 = p2
        cx3, cy3 = p3
        
        # Path values: (Logo1 -> Logo1 -> Logo1 -> Logo2 -> Logo2 -> Logo3 -> Logo3 -> Logo1 -> Logo1)
        cx_vals = f"{cx1}; {cx1}; {cx1}; {cx1}; {cx2}; {cx2}; {cx3}; {cx3}; {cx1}"
        cy_vals = f"{cy1}; {cy1}; {cy1}; {cy1}; {cy2}; {cy2}; {cy3}; {cy3}; {cy1}"
        
        svg.append(f'<circle class="traveller" r="1.2">')
        svg.append(f'  <animate attributeName="cx" values="{cx_vals}" keyTimes="{keytimes_str}" dur="14.2s" begin="2.0s" repeatCount="indefinite"/>')
        svg.append(f'  <animate attributeName="cy" values="{cy_vals}" keyTimes="{keytimes_str}" dur="14.2s" begin="2.0s" repeatCount="indefinite"/>')
        svg.append(f'</circle>')
        
    svg.append('</g>')
    
    # Right Side SYSTEM.INFO Panel
    svg.append('<g transform="translate(420, 80)">')
    svg.append(f'<text x="0" y="0" fill="{chrome_color}" font-size="13" font-weight="bold">SYSTEM.INFO</text>')
    
    # LIVE badge
    svg.append('<g transform="translate(650, -10)">')
    svg.append('<circle cx="5" cy="5" r="4" fill="#EF4444" class="pulse"/>')
    svg.append(f'<text x="15" y="9" fill="#EF4444" font-size="12" font-weight="bold">LIVE</text>')
    svg.append('</g>')
    
    info_data = [
        ("Subject", "Afnaan Ahmed P"),
        ("Role", "AI/ML Engineer, Backend Developer"),
        ("Origin", "Chennai, India"),
        ("Education", "MTech Integrated SE @ VIT"),
        ("Status", "Building + Learning + Shipping"),
        ("ToolChain", "VS Code, Git, Docker, Figma"),
        ("Core.Lang", "Python, JS, TS, Go, Java, C"),
        ("Core.Frontend", "React, HTML5, CSS3"),
        ("Core.Backend", "FastAPI, Node.js, Express"),
        ("Core.Database", "PostgreSQL, MongoDB, Redis"),
        ("Core.Infra", "AWS, Docker, K8s, CI/CD"),
        ("Grid.Mail", "Afnaanahmed.k391@gmail.com"),
        ("Grid.Portfolio", "https://22mis1157.github.io/"),
        ("Grid.LinkedIn", "afnaan22mis1157"),
        ("Grid.GitHub", "22MIS1157")
    ]
    
    y_offset = 40
    for label, value in info_data:
        dots = "." * max(2, 65 - len(label) - len(value))
        svg.append(f'<text x="0" y="{y_offset}" fill="{chrome_color}" font-size="14">{label}</text>')
        svg.append(f'<text x="{len(label)*8 + 5}" y="{y_offset}" fill="{chrome_color}" font-size="14" opacity="0.3" textLength="{len(dots)*8}" lengthAdjust="spacingAndGlyphs">{dots}</text>')
        svg.append(f'<text x="520" y="{y_offset}" fill="{text_color}" font-size="14" text-anchor="end">{value}</text>')
        y_offset += 23
        
    svg.append('</g>')
    
    # Footer Note
    svg.append(f'<text x="40" y="580" fill="{chrome_color}" font-size="11" opacity="0.5">• More about me &amp; projects below in README ↓</text>')
    svg.append('</svg>')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(svg))
    print(f"Generated {output_path}")

def main():
    print("[morph] Extracting points from logos...")
    logo1 = extract_logo_points(AKATSUKI_PATH, num_points=650)
    logo2 = extract_logo_points(ONEPIECE_PATH, num_points=650)
    logo3 = extract_logo_points(DEADPOOL_PATH, num_points=650)
    
    print("[morph] Processing portrait image...")
    dark_portrait = process_portrait(PHOTO_PATH, is_dark=True)
    light_portrait = process_portrait(PHOTO_PATH, is_dark=False)
    
    palettes = {
        "dark": {
            'Portrait dots': '#A78BFA',
            'UI chrome': '#22D3EE',
            'Accent': '#10B981',
            'Background': '#0A101F',
            'Text': '#94A3B8'
        },
        "light": {
            'Portrait dots': '#7C3AED',
            'UI chrome': '#0891B2',
            'Accent': '#10B981',
            'Background': '#FFFFFF',
            'Text': '#475569'
        }
    }
    
    output_dir = ROOT
    print("[morph] Generating dark mode morphing SVG...")
    generate_svg(dark_portrait, logo1, logo2, logo3, palettes['dark'], True, os.path.join(output_dir, "dark.svg"))
    
    print("[morph] Generating light mode morphing SVG...")
    generate_svg(light_portrait, logo1, logo2, logo3, palettes['light'], False, os.path.join(output_dir, "light.svg"))

if __name__ == "__main__":
    main()
