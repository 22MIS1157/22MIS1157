"""
Final Custom Banner Generator:
Sequence:
1. Girigo Logo ('A' Emblem / Praying Hands) - 0.0s to 4.0s
2. User Photo (Afnaan's Portrait) - 4.0s to 8.0s
3. Coding Logo ('</>' Code Glyph) - 8.0s to 12.0s
Loop duration: 12.0s
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
GIRIGO_PATH = os.path.join(BRAIN_USER, "media__1785342103463.png")

PORTRAIT_W = 290
PORTRAIT_H = 350
NUM_TRAVELLERS = 1200

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

def extract_girigo_points(img_path, num_points=1200, target_w=290, target_h=350):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    aspect = w / h
    if aspect > (target_w / target_h):
        nw = target_w - 20
        nh = int(nw / aspect)
    else:
        nh = target_h - 20
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
            if a > 40 and (r > 140 and g > 140 and b > 140):
                points.append((x, y))
                
    if len(points) == 0:
        points = [(target_w//2, target_h//2)]
        
    rnd = random.Random(42)
    if len(points) >= num_points:
        points = rnd.sample(points, num_points)
    else:
        while len(points) < num_points:
            p = rnd.choice(points)
            points.append((p[0] + rnd.randint(-1, 1), p[1] + rnd.randint(-1, 1)))
            
    return np.array(points)

def generate_code_glyph(num_points=1200, w=290, h=350):
    cx, cy = w / 2, h / 2
    pts = []
    n_part = num_points // 3
    # '<'
    for t in np.linspace(0, 1, n_part):
        x = cx - 50 - (1 - abs(t - 0.5)*2) * 55
        y = cy - 65 + t * 130
        pts.append((x, y))
    # '/'
    for t in np.linspace(0, 1, n_part):
        x = cx + 22 - t * 44
        y = cy - 75 + t * 150
        pts.append((x, y))
    # '>'
    for t in np.linspace(0, 1, n_part):
        x = cx + 50 + (1 - abs(t - 0.5)*2) * 55
        y = cy - 65 + t * 130
        pts.append((x, y))
    return np.array(pts[:num_points])

def align_points(pts_a, pts_b):
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
    target_ratio = PORTRAIT_W / float(PORTRAIT_H)
    img_ratio = w / h
    if img_ratio > target_ratio:
        new_w = int(h * target_ratio)
        offset = (w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, h))
    else:
        new_h = int(w / target_ratio)
        offset = (h - new_h) // 2
        img = img.crop((0, offset, w, offset + new_h))
        
    img = img.resize((PORTRAIT_W, PORTRAIT_H), Image.Resampling.LANCZOS)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=150))
    
    if is_dark:
        img = ImageOps.invert(img)
        
    return floyd_steinberg_dither(img)

def generate_svg(dot_matrix, girigo_pts, code_pts, palette, is_dark, output_path):
    bg_color = palette['Background']
    chrome_color = palette['UI chrome']
    dot_color = palette['Portrait dots']
    text_color = palette['Text']
    pill_color = palette['Pill']
    
    h = len(dot_matrix)
    w = len(dot_matrix[0])
    
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
    
    svg.append('<style>')
    svg.append('.pulse { animation: p 2s infinite; }')
    svg.append('@keyframes p { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }')
    svg.append('.corner-glow { stroke: ' + chrome_color + '; stroke-width: 2; fill: none; filter: drop-shadow(0 0 3px ' + chrome_color + '); }')
    svg.append('</style>')
    
    # Outer Terminal Frame
    svg.append(f'<rect x="10" y="10" width="1160" height="590" rx="12" ry="12" fill="none" stroke="{chrome_color}" stroke-width="1.5" opacity="0.6"/>')
    svg.append(f'<line x1="10" y1="42" x2="1170" y2="42" stroke="{chrome_color}" stroke-width="1" opacity="0.3"/>')
    
    # Traffic Light Buttons
    svg.append('<circle cx="32" cy="26" r="5" fill="#FF5F56"/>')
    svg.append('<circle cx="48" cy="26" r="5" fill="#FFBD2E"/>')
    svg.append('<circle cx="64" cy="26" r="5" fill="#27C93F"/>')
    
    # Terminal Title Centered
    svg.append(f'<text x="590" y="30" fill="{text_color}" font-size="13" text-anchor="middle" opacity="0.8">Afnaanahmed.k391@gmail.com - % ./profile.sh --live</text>')
    
    # VISUAL.MAP Frame
    box_x, box_y, box_w, box_h = 45, 65, 330, 420
    svg.append(f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" fill="none" stroke="{chrome_color}" stroke-width="1" opacity="0.25"/>')
    svg.append(f'<text x="58" y="85" fill="{text_color}" font-size="11" opacity="0.6">VISUAL.MAP</text>')
    
    # Glowing Corner Brackets
    svg.append(f'<path class="corner-glow" d="M38,85 V60 H63"/>')
    svg.append(f'<path class="corner-glow" d="M382,85 V60 H357"/>')
    svg.append(f'<path class="corner-glow" d="M38,465 V490 H63"/>')
    svg.append(f'<path class="corner-glow" d="M382,465 V490 H357"/>')
    
    # Footer Arrow Note
    svg.append(f'<text x="45" y="525" fill="{chrome_color}" font-size="12" opacity="0.8">► More about me &amp; projects below in README ↓</text>')
    
    # --- Timing for 12.0s Loop ---
    # 0.0s - 3.5s (0.000 to 0.292): Stage 1 -> Girigo Logo (Layer 2)
    # 3.5s - 4.0s (0.292 to 0.333): Transition to Stage 2
    # 4.0s - 7.5s (0.333 to 0.625): Stage 2 -> User Photo (Layer 1)
    # 7.5s - 8.0s (0.625 to 0.667): Transition to Stage 3
    # 8.0s - 11.5s (0.667 to 0.958): Stage 3 -> Coding Logo (Layer 2)
    # 11.5s - 12.0s (0.958 to 1.000): Transition back to Stage 1 (Girigo Logo)
    
    portrait_offset_x = 65
    portrait_offset_y = 100
    
    # Layer 1: User Photo
    keytimes_l1 = "0; 0.292; 0.333; 0.625; 0.667; 1"
    opacity_l1 = "0; 0; 1; 1; 0; 0"
    
    svg.append(f'<g transform="translate({portrait_offset_x}, {portrait_offset_y})">')
    for b_idx in range(num_bands):
        if not bands_data[b_idx]:
            continue
            
        path_str = " ".join(bands_data[b_idx])
        dx = rnd.uniform(-40, 40)
        dy = rnd.uniform(-25, 25)
        trans_vals = f"{dx:.1f},{dy:.1f}; {dx:.1f},{dy:.1f}; 0,0; 0,0; {dx:.1f},{dy:.1f}; {dx:.1f},{dy:.1f}"
        
        svg.append('<g>')
        svg.append(f'  <animate attributeName="opacity" values="{opacity_l1}" keyTimes="{keytimes_l1}" dur="12.0s" repeatCount="indefinite"/>')
        svg.append(f'  <animateTransform attributeName="transform" type="translate" values="{trans_vals}" keyTimes="{keytimes_l1}" dur="12.0s" repeatCount="indefinite"/>')
        svg.append(f'  <path stroke="{dot_color}" stroke-width="1.8" shape-rendering="crispEdges" d="{path_str}"/>')
        svg.append('</g>')
    svg.append('</g>')
    
    # Layer 2: Travellers (Girigo Logo ➔ User Photo [hidden] ➔ Coding Logo ➔ Girigo Logo)
    keytimes_l2 = "0; 0.292; 0.333; 0.625; 0.667; 0.958; 1"
    opacity_l2 = "0.98; 0.98; 0; 0; 0.98; 0.98; 0.98"
    
    cx0, cy0 = PORTRAIT_W // 2, PORTRAIT_H // 2
    
    svg.append(f'<g transform="translate({portrait_offset_x}, {portrait_offset_y})">')
    for i in range(len(girigo_pts)):
        x1, y1 = girigo_pts[i]
        x2, y2 = code_pts[i]
        
        cx_vals = f"{x1:.1f}; {x1:.1f}; {cx0}; {cx0}; {x2:.1f}; {x2:.1f}; {x1:.1f}"
        cy_vals = f"{y1:.1f}; {y1:.1f}; {cy0}; {cy0}; {y2:.1f}; {y2:.1f}; {y1:.1f}"
        
        svg.append(f'<circle r="2.0" fill="{dot_color}">')
        svg.append(f'  <animate attributeName="opacity" values="{opacity_l2}" keyTimes="{keytimes_l2}" dur="12.0s" repeatCount="indefinite"/>')
        svg.append(f'  <animate attributeName="cx" values="{cx_vals}" keyTimes="{keytimes_l2}" dur="12.0s" repeatCount="indefinite"/>')
        svg.append(f'  <animate attributeName="cy" values="{cy_vals}" keyTimes="{keytimes_l2}" dur="12.0s" repeatCount="indefinite"/>')
        svg.append(f'</circle>')
    svg.append('</g>')
    
    # --- Right Side SYSTEM.INFO Panel ---
    svg.append('<g transform="translate(420, 85)">')
    svg.append(f'<text x="0" y="0" fill="{chrome_color}" font-size="13" font-weight="bold">SYSTEM.INFO</text>')
    
    # LIVE badge
    svg.append('<g transform="translate(640, -10)">')
    svg.append('<circle cx="5" cy="5" r="4" fill="#EF4444" class="pulse"/>')
    svg.append(f'<text x="15" y="9" fill="#EF4444" font-size="12" font-weight="bold">LIVE</text>')
    svg.append('</g>')
    
    # Email Pill Badge
    svg.append(f'<g transform="translate(0, 18)">')
    svg.append(f'<rect x="0" y="0" width="220" height="26" rx="4" fill="{pill_color}"/>')
    svg.append(f'<text x="110" y="18" fill="white" font-size="13" text-anchor="middle" font-weight="bold">Afnaanahmed.k391@gmail.com</text>')
    svg.append(f'</g>')
    
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
        ("- Contact", ""),
        ("Grid.Mail", "Afnaanahmed.k391@gmail.com"),
        ("Grid.Portfolio", "https://22mis1157.github.io/"),
        ("Grid.LinkedIn", "afnaan22mis1157"),
        ("Grid.GitHub", "@22MIS1157")
    ]
    
    y_offset = 70
    for label, value in info_data:
        if label == "- Contact":
            svg.append(f'<text x="0" y="{y_offset}" fill="{text_color}" font-size="13" opacity="0.6">- Contact</text>')
            y_offset += 24
            continue
            
        dots = "." * max(2, 65 - len(label) - len(value))
        svg.append(f'<text x="0" y="{y_offset}" fill="{chrome_color}" font-size="14">{label}</text>')
        svg.append(f'<text x="{len(label)*8 + 5}" y="{y_offset}" fill="{chrome_color}" font-size="14" opacity="0.3" textLength="{len(dots)*8}" lengthAdjust="spacingAndGlyphs">{dots}</text>')
        svg.append(f'<text x="520" y="{y_offset}" fill="{text_color}" font-size="14" text-anchor="end">{value}</text>')
        y_offset += 23
        
    svg.append('</g>')
    svg.append('</svg>')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(svg))
    print(f"Generated {output_path}")

def main():
    print("Generating exact requested order: 1. Girigo Logo -> 2. User Photo -> 3. Coding Logo...")
    girigo_pts = extract_girigo_points(GIRIGO_PATH, num_points=NUM_TRAVELLERS)
    code_pts_raw = generate_code_glyph(num_points=NUM_TRAVELLERS)
    
    print("Running Hungarian optimal transport alignment...")
    code_pts = align_points(girigo_pts, code_pts_raw)
    
    print("Processing portrait photo...")
    dark_portrait = process_portrait(PHOTO_PATH, is_dark=True)
    light_portrait = process_portrait(PHOTO_PATH, is_dark=False)
    
    palettes = {
        "dark": {
            'Portrait dots': '#A78BFA',
            'UI chrome': '#22D3EE',
            'Pill': '#7C3AED',
            'Background': '#0A101F',
            'Text': '#94A3B8'
        },
        "light": {
            'Portrait dots': '#7C3AED',
            'UI chrome': '#0891B2',
            'Pill': '#7C3AED',
            'Background': '#FFFFFF',
            'Text': '#475569'
        }
    }
    
    print("Building dark.svg...")
    generate_svg(dark_portrait, girigo_pts, code_pts, palettes['dark'], True, os.path.join(ROOT, "dark.svg"))
    
    print("Building light.svg...")
    generate_svg(light_portrait, girigo_pts, code_pts, palettes['light'], False, os.path.join(ROOT, "light.svg"))

if __name__ == "__main__":
    main()
