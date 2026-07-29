"""
Master SMIL Banner Generator v3 with Procedural Vector Logos:
- 100% Crisp & Iconic Procedural Vector Geometry for 3 Logos:
  1. Sharingan Eye 👁️ (Naruto Tomoe Ring & Pupil)
  2. </ > Programmer Code Glyph 💻 (Brackets & Slash)
  3. One Piece Strawhat Jolly Roger 🏴‍☠️ (Skull & Crossbones)
- Hungarian Optimal Transport alignment between all 3 logos for fluid particle morphing.
- High-density Floyd-Steinberg dithered portrait (Layer 1) visible instantly on load.
- Terminal UI with glowing cyan corner brackets, macOS traffic light buttons, and purple email pill.
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

PORTRAIT_W = 290
PORTRAIT_H = 350
NUM_TRAVELLERS = 900

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

def generate_sharingan(num_points=900, w=290, h=350):
    cx, cy = w / 2, h / 2
    pts = []
    
    # Outer circle
    r_outer = 85
    n_out = int(num_points * 0.35)
    for theta in np.linspace(0, 2*math.pi, n_out, endpoint=False):
        pts.append((cx + r_outer * math.cos(theta), cy + r_outer * math.sin(theta)))
        
    # Inner tomoe ring
    r_ring = 54
    n_ring = int(num_points * 0.25)
    for theta in np.linspace(0, 2*math.pi, n_ring, endpoint=False):
        pts.append((cx + r_ring * math.cos(theta), cy + r_ring * math.sin(theta)))
        
    # Center pupil
    n_pupil = int(num_points * 0.15)
    rnd = random.Random(42)
    for _ in range(n_pupil):
        r = rnd.uniform(0, 18)
        theta = rnd.uniform(0, 2*math.pi)
        pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
        
    # 3 Tomoe commas (0, 120, 240 deg)
    n_tomoe = (num_points - len(pts)) // 3
    for angle_deg in [0, 120, 240]:
        base_angle = math.radians(angle_deg)
        tx = cx + r_ring * math.cos(base_angle)
        ty = cy + r_ring * math.sin(base_angle)
        for _ in range(n_tomoe):
            rh = rnd.uniform(0, 10)
            th = rnd.uniform(0, 2*math.pi)
            pts.append((tx + rh * math.cos(th), ty + rh * math.sin(th)))
            
    while len(pts) < num_points:
        pts.append(pts[-1])
    return np.array(pts[:num_points])

def generate_code_glyph(num_points=900, w=290, h=350):
    cx, cy = w / 2, h / 2
    pts = []
    n_part = num_points // 3
    # '<'
    for t in np.linspace(0, 1, n_part):
        x = cx - 45 - (1 - abs(t - 0.5)*2) * 50
        y = cy - 60 + t * 120
        pts.append((x, y))
    # '/'
    for t in np.linspace(0, 1, n_part):
        x = cx + 20 - t * 40
        y = cy - 70 + t * 140
        pts.append((x, y))
    # '>'
    for t in np.linspace(0, 1, n_part):
        x = cx + 45 + (1 - abs(t - 0.5)*2) * 50
        y = cy - 60 + t * 120
        pts.append((x, y))
        
    while len(pts) < num_points:
        pts.append(pts[-1])
    return np.array(pts[:num_points])

def generate_onepiece(num_points=900, w=290, h=350):
    cx, cy = w / 2, h / 2
    pts = []
    
    # Crossbones (X shape)
    n_bones = int(num_points * 0.35)
    for t in np.linspace(0, 1, n_bones // 2):
        pts.append((cx - 80 + t * 160, cy - 80 + t * 160))
        pts.append((cx - 80 + t * 160, cy + 80 - t * 160))
        
    # Skull Head
    n_skull = int(num_points * 0.3)
    for theta in np.linspace(0, 2*math.pi, n_skull, endpoint=False):
        pts.append((cx + 40 * math.cos(theta), cy + 12 + 40 * math.sin(theta)))
        
    # Straw Hat Dome
    n_hat = int(num_points * 0.2)
    for theta in np.linspace(math.pi*0.8, math.pi*2.2, n_hat):
        pts.append((cx + 45 * math.cos(theta), cy - 18 + 35 * math.sin(theta)))
        
    # Straw Hat Brim
    n_brim = num_points - len(pts)
    for t in np.linspace(-70, 70, n_brim):
        pts.append((cx + t, cy - 12))
        
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
    
    # CSS Styles
    svg.append('<style>')
    svg.append('.pulse { animation: p 2s infinite; }')
    svg.append('@keyframes p { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }')
    svg.append('.corner-glow { stroke: ' + chrome_color + '; stroke-width: 2; fill: none; filter: drop-shadow(0 0 3px ' + chrome_color + '); }')
    svg.append('</style>')
    
    # Outer Terminal Frame
    svg.append(f'<rect x="10" y="10" width="1160" height="590" rx="12" ry="12" fill="none" stroke="{chrome_color}" stroke-width="1.5" opacity="0.6"/>')
    svg.append(f'<line x1="10" y1="42" x2="1170" y2="42" stroke="{chrome_color}" stroke-width="1" opacity="0.3"/>')
    
    # Traffic Light Buttons (Red, Yellow, Green)
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
    
    # --- Layer 1: Portrait Bands ---
    # Timing (14.2s loop matching PDF):
    # 0s -> 3.0s (0.211): 100% visible
    # 3.0s -> 4.3s (0.303): dissolve to opacity 0
    # 4.3s -> 12.9s (0.908): opacity 0
    # 12.9s -> 14.2s (1.000): return to opacity 1
    
    keytimes_l1 = "0; 0.211; 0.303; 0.908; 1"
    opacity_l1 = "1; 1; 0; 0; 1"
    
    portrait_offset_x = 65
    portrait_offset_y = 100
    
    svg.append(f'<g transform="translate({portrait_offset_x}, {portrait_offset_y})">')
    for b_idx in range(num_bands):
        if not bands_data[b_idx]:
            continue
            
        path_str = " ".join(bands_data[b_idx])
        dx = rnd.uniform(-50, 50)
        dy = rnd.uniform(-30, 30)
        trans_vals = f"0,0; 0,0; {dx:.1f},{dy:.1f}; {dx:.1f},{dy:.1f}; 0,0"
        
        svg.append('<g>')
        svg.append(f'  <animate attributeName="opacity" values="{opacity_l1}" keyTimes="{keytimes_l1}" dur="14.2s" repeatCount="indefinite"/>')
        svg.append(f'  <animateTransform attributeName="transform" type="translate" values="{trans_vals}" keyTimes="{keytimes_l1}" dur="14.2s" repeatCount="indefinite"/>')
        svg.append(f'  <path stroke="{dot_color}" stroke-width="1" shape-rendering="crispEdges" d="{path_str}"/>')
        svg.append('</g>')
    svg.append('</g>')
    
    # --- Layer 2: Travellers (Morphing across 3 Procedural Logos) ---
    # KeyTimes (14.2s loop):
    # 0s -> 3.0s (0.211): hidden (opacity 0)
    # 4.3s (0.303): Form Logo 1 (Sharingan Eye) - opacity 1
    # 6.3s (0.444): Hold Logo 1 -> morph to Logo 2 (</> Code Glyph)
    # 7.6s (0.535): Form Logo 2 (</> Code Glyph)
    # 9.6s (0.676): Hold Logo 2 -> morph to Logo 3 (One Piece Skull)
    # 10.9s (0.768): Form Logo 3 (One Piece Skull)
    # 12.9s (0.908): Hold Logo 3 -> return to center
    # 14.2s (1.000): hidden
    
    keytimes_l2 = "0; 0.211; 0.303; 0.444; 0.535; 0.676; 0.768; 0.908; 1"
    opacity_l2 = "0; 0; 0.95; 0.95; 0.95; 0.95; 0.95; 0; 0"
    
    cx0, cy0 = PORTRAIT_W // 2, PORTRAIT_H // 2
    
    svg.append(f'<g transform="translate({portrait_offset_x}, {portrait_offset_y})">')
    for i in range(len(logo1_pts)):
        x1, y1 = logo1_pts[i]
        x2, y2 = logo2_pts[i]
        x3, y3 = logo3_pts[i]
        
        cx_vals = f"{cx0}; {cx0}; {x1:.1f}; {x1:.1f}; {x2:.1f}; {x2:.1f}; {x3:.1f}; {x3:.1f}; {cx0}"
        cy_vals = f"{cy0}; {cy0}; {y1:.1f}; {y1:.1f}; {y2:.1f}; {y2:.1f}; {y3:.1f}; {y3:.1f}; {cy0}"
        
        svg.append(f'<circle r="1.3" fill="{dot_color}">')
        svg.append(f'  <animate attributeName="opacity" values="{opacity_l2}" keyTimes="{keytimes_l2}" dur="14.2s" repeatCount="indefinite"/>')
        svg.append(f'  <animate attributeName="cx" values="{cx_vals}" keyTimes="{keytimes_l2}" dur="14.2s" repeatCount="indefinite"/>')
        svg.append(f'  <animate attributeName="cy" values="{cy_vals}" keyTimes="{keytimes_l2}" dur="14.2s" repeatCount="indefinite"/>')
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
    
    # Email Pill Badge (Purple like arifhaxn's screenshot!)
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
    print(f"Successfully generated {output_path}")

def main():
    print("[v3] Generating procedural vector logos...")
    pts1 = generate_sharingan(num_points=NUM_TRAVELLERS)
    pts2_raw = generate_code_glyph(num_points=NUM_TRAVELLERS)
    pts3_raw = generate_onepiece(num_points=NUM_TRAVELLERS)
    
    print("[v3] Running Hungarian optimal transport point alignment...")
    pts2 = align_points(pts1, pts2_raw)
    pts3 = align_points(pts2, pts3_raw)
    
    print("[v3] Processing portrait photo...")
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
    
    print("[v3] Building dark.svg...")
    generate_svg(dark_portrait, pts1, pts2, pts3, palettes['dark'], True, os.path.join(ROOT, "dark.svg"))
    
    print("[v3] Building light.svg...")
    generate_svg(light_portrait, pts1, pts2, pts3, palettes['light'], False, os.path.join(ROOT, "light.svg"))

if __name__ == "__main__":
    main()
