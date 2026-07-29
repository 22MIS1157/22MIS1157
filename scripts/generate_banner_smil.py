"""
Complete SMIL Banner Generator implementing Master Prompt PDF specifications:
- Two-layer architecture:
  Layer 1: Floyd-Steinberg dithered portrait (~17k dots) grouped into drift bands.
           Drifts outward and fades out while logos show, then returns.
  Layer 2: Travellers (~900 dots) matched by optimal transport across 3 logos:
           Akatsuki Cloud -> One Piece Strawhat Jolly Roger -> Deadpool Logo.
           Hidden during portrait phase, visible & morphing during logo phases.
- SMIL animations natively embedded (no CSS specificity conflicts).
"""
import os
import random
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from scipy.optimize import linear_sum_assignment

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
NUM_TRAVELLERS = 850

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

def extract_logo_points(img_path, num_points=850, target_w=280, target_h=320):
    img = Image.open(img_path).convert("RGBA")
    
    w, h = img.size
    aspect = w / h
    if aspect > (target_w / target_h):
        nw = target_w - 30
        nh = int(nw / aspect)
    else:
        nh = target_h - 30
        nw = int(nh * aspect)
        
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    px = (target_w - nw) // 2
    py = (target_h - nh) // 2
    canvas.paste(img, (px, py), img)
    
    arr = np.array(canvas)
    points = []
    
    for y in range(target_h):
        for x in range(target_w):
            r, g, b, a = arr[y, x]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            # Include visible pixels with non-transparent alpha
            if a > 40 and lum < 235:
                points.append((x, y))
                
    if len(points) == 0:
        points = [(target_w//2, target_h//2)]
        
    rnd = random.Random(101)
    if len(points) >= num_points:
        points = rnd.sample(points, num_points)
    else:
        while len(points) < num_points:
            p = rnd.choice(points)
            points.append((p[0] + rnd.randint(-1, 1), p[1] + rnd.randint(-1, 1)))
            
    return np.array(points)

def align_points_optimal_transport(pts_a, pts_b):
    """Align pts_b to pts_a using linear sum assignment for shortest morph distance."""
    cost = np.linalg.norm(pts_a[:, None, :] - pts_b[None, :, :], axis=2)
    row_ind, col_ind = linear_sum_assignment(cost)
    return pts_b[col_ind]

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
    
    h = len(dot_matrix)
    w = len(dot_matrix[0])
    
    # 94 Drift Bands for Layer 1 Portrait
    num_bands = 94
    bands_data = {i: [] for i in range(num_bands)}
    rnd = random.Random(42)
    
    for y in range(h):
        run_start = -1
        for x in range(w):
            if dot_matrix[y][x] == 1:
                if run_start == -1:
                    run_start = x
            else:
                if run_start != -1:
                    b = rnd.randint(0, num_bands - 1)
                    bands_data[b].append(f"M{run_start},{y}h{x - run_start}")
                    run_start = -1
        if run_start != -1:
            b = rnd.randint(0, num_bands - 1)
            bands_data[b].append(f"M{run_start},{y}h{w - run_start}")
            
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610" style="background-color: {bg_color}; font-family: monospace;">')
    
    # CSS Styles
    svg.append('<style>')
    svg.append('.pulse { animation: p 2s infinite; }')
    svg.append('@keyframes p { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }')
    svg.append('</style>')
    
    # Terminal Frame
    svg.append(f'<rect x="10" y="10" width="1160" height="590" fill="none" stroke="{chrome_color}" stroke-width="2"/>')
    svg.append(f'<rect x="10" y="10" width="1160" height="30" fill="{chrome_color}" opacity="0.1"/>')
    svg.append(f'<text x="25" y="30" fill="{chrome_color}" font-size="14" font-weight="bold">profile.sh --live</text>')
    
    # Handle pill badge
    svg.append(f'<g transform="translate(960, 13)">')
    svg.append(f'<rect x="0" y="0" width="180" height="24" rx="12" fill="{accent_color}" opacity="0.9"/>')
    svg.append(f'<text x="90" y="16" fill="white" font-size="14" text-anchor="middle" font-weight="bold">@22MIS1157</text>')
    svg.append(f'</g>')
    
    # Portrait Container
    svg.append(f'<rect x="40" y="60" width="340" height="380" fill="none" stroke="{chrome_color}" stroke-width="1" opacity="0.5"/>')
    svg.append(f'<text x="40" y="460" fill="{chrome_color}" font-size="12">VISUAL.MAP</text>')
    svg.append(f'<text x="210" y="460" fill="{text_color}" font-size="11" text-anchor="middle" opacity="0.7">Morphing: Portrait ➔ Akatsuki ➔ One Piece ➔ Deadpool</text>')
    
    # Layer 1: Portrait Bands (~94 bands with drift translation + SMIL fade)
    svg.append('<g transform="translate(70, 90)">')
    
    # Keytimes & values for 14.2s loop
    # t=0s -> 0.000 (intro start, opacity 0->1)
    # t=2.0s -> 0.141 (intro end, portrait fully visible)
    # t=3.0s -> 0.211 (portrait hold end, start dissolve)
    # t=4.3s -> 0.303 (fully dissolved / opacity 0)
    # t=12.9s -> 0.908 (logos end, start return)
    # t=14.2s -> 1.000 (portrait fully returned)
    
    keytimes_layer1 = "0; 0.141; 0.211; 0.303; 0.908; 1"
    opacity_layer1 = "0; 1; 1; 0; 0; 1"
    
    for b_idx in range(num_bands):
        if not bands_data[b_idx]:
            continue
            
        path_str = " ".join(bands_data[b_idx])
        
        # Calculate random drift vector for band (~42% toward centroid + noise)
        dx = rnd.uniform(-60, 60)
        dy = rnd.uniform(-40, 40)
        
        trans_values = f"0,0; 0,0; 0,0; {dx:.1f},{dy:.1f}; {dx:.1f},{dy:.1f}; 0,0"
        
        svg.append('<g>')
        svg.append(f'  <animate attributeName="opacity" values="{opacity_layer1}" keyTimes="{keytimes_layer1}" dur="14.2s" repeatCount="indefinite"/>')
        svg.append(f'  <animateTransform attributeName="transform" type="translate" values="{trans_values}" keyTimes="{keytimes_layer1}" dur="14.2s" repeatCount="indefinite"/>')
        svg.append(f'  <path stroke="{dot_color}" stroke-width="1" shape-rendering="crispEdges" d="{path_str}"/>')
        svg.append('</g>')
        
    svg.append('</g>')
    
    # Layer 2: Travellers (850 dots morphing across 3 logos via Optimal Transport)
    # KeyTimes:
    # 0s (0.000): hidden
    # 3.0s (0.211): hidden -> start morphing to Logo 1 (Akatsuki)
    # 4.3s (0.303): Logo 1 (Akatsuki)
    # 6.3s (0.444): Hold Logo 1 -> morph to Logo 2 (One Piece)
    # 7.6s (0.535): Logo 2 (One Piece)
    # 9.6s (0.676): Hold Logo 2 -> morph to Logo 3 (Deadpool)
    # 10.9s (0.768): Logo 3 (Deadpool)
    # 12.9s (0.908): Hold Logo 3 -> morph back & fade out
    # 14.2s (1.000): hidden
    
    keytimes_layer2 = "0; 0.211; 0.303; 0.444; 0.535; 0.676; 0.768; 0.908; 1"
    opacity_layer2 = "0; 0; 0.95; 0.95; 0.95; 0.95; 0.95; 0; 0"
    
    center_x, center_y = 140, 160
    
    svg.append('<g transform="translate(70, 90)">')
    for i in range(len(logo1_pts)):
        x1, y1 = logo1_pts[i]
        x2, y2 = logo2_pts[i]
        x3, y3 = logo3_pts[i]
        
        cx_vals = f"{center_x}; {center_x}; {x1}; {x1}; {x2}; {x2}; {x3}; {x3}; {center_x}"
        cy_vals = f"{center_y}; {center_y}; {y1}; {y1}; {y2}; {y2}; {y3}; {y3}; {center_y}"
        
        svg.append(f'<circle r="1.3" fill="{dot_color}">')
        svg.append(f'  <animate attributeName="opacity" values="{opacity_layer2}" keyTimes="{keytimes_layer2}" dur="14.2s" repeatCount="indefinite"/>')
        svg.append(f'  <animate attributeName="cx" values="{cx_vals}" keyTimes="{keytimes_layer2}" dur="14.2s" repeatCount="indefinite"/>')
        svg.append(f'  <animate attributeName="cy" values="{cy_vals}" keyTimes="{keytimes_layer2}" dur="14.2s" repeatCount="indefinite"/>')
        svg.append(f'</circle>')
        
    svg.append('</g>')
    
    # Right Side SYSTEM.INFO Readout
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
    print(f"Successfully generated {output_path}")

def main():
    print("[smil] Extracting points from 3 logos...")
    pts1 = extract_logo_points(AKATSUKI_PATH, num_points=NUM_TRAVELLERS)
    pts2_raw = extract_logo_points(ONEPIECE_PATH, num_points=NUM_TRAVELLERS)
    pts3_raw = extract_logo_points(DEADPOOL_PATH, num_points=NUM_TRAVELLERS)
    
    print("[smil] Running Optimal Transport point alignment (Hungarian Algorithm)...")
    pts2 = align_points_optimal_transport(pts1, pts2_raw)
    pts3 = align_points_optimal_transport(pts2, pts3_raw)
    
    print("[smil] Processing portrait photo...")
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
    
    print("[smil] Building dark.svg...")
    generate_svg(dark_portrait, pts1, pts2, pts3, palettes['dark'], True, os.path.join(ROOT, "dark.svg"))
    
    print("[smil] Building light.svg...")
    generate_svg(light_portrait, pts1, pts2, pts3, palettes['light'], False, os.path.join(ROOT, "light.svg"))

if __name__ == "__main__":
    main()
