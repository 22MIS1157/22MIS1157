import os
import random
import math
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
try:
    from rembg import remove
except ImportError:
    print("Please install rembg: pip install rembg")
    import sys
    sys.exit(1)

def floyd_steinberg_dither(img, serpentine=True):
    pixels = img.load()
    w, h = img.size
    
    # Threshold array
    result = [[0 for _ in range(w)] for _ in range(h)]
    
    for y in range(h):
        direction = 1 if (not serpentine or y % 2 == 0) else -1
        start_x = 0 if direction == 1 else w - 1
        end_x = w if direction == 1 else -1
        
        for x in range(start_x, end_x, direction):
            oldpixel = pixels[x, y]
            newpixel = 255 if oldpixel > 127 else 0
            pixels[x, y] = newpixel
            result[y][x] = 1 if newpixel == 0 else 0 # 1 means dot, 0 means no dot
            
            quant_error = oldpixel - newpixel
            
            # distribute error
            def add_error(nx, ny, factor):
                if 0 <= nx < w and 0 <= ny < h:
                    pixels[nx, ny] = min(max(int(pixels[nx, ny] + quant_error * factor), 0), 255)

            if direction == 1:
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

def generate_svg(dot_matrix, palette, is_dark, output_path):
    # Animation setup
    num_groups = 60
    
    # Path runs optimization
    paths_by_group = {i: [] for i in range(num_groups)}
    
    h = len(dot_matrix)
    w = len(dot_matrix[0]) if h > 0 else 0
    
    for y in range(h):
        run_start = -1
        for x in range(w):
            if dot_matrix[y][x] == 1:
                if run_start == -1:
                    run_start = x
            else:
                if run_start != -1:
                    group = random.randint(0, num_groups - 1)
                    paths_by_group[group].append(f"M{run_start},{y}h{x - run_start}")
                    run_start = -1
        if run_start != -1:
            group = random.randint(0, num_groups - 1)
            paths_by_group[group].append(f"M{run_start},{y}h{w - run_start}")
            
    # SVG Strings
    bg_color = palette['Background']
    chrome_color = palette['UI chrome']
    dot_color = palette['Portrait dots']
    text_color = palette['Text']
    accent_color = palette['Accent']
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610" style="background-color: {bg_color}; font-family: monospace;">')
    
    # Styles for animation
    svg.append('<style>')
    svg.append('.d { stroke: ' + dot_color + '; stroke-width: 1; shape-rendering: crispEdges; opacity: 0; animation: fadein 0.5s forwards; }')
    svg.append('@keyframes fadein { from { opacity: 0; } to { opacity: 1; } }')
    
    for i in range(num_groups):
        delay = (i / num_groups) * 2.0
        svg.append(f'.g{i} {{ animation-delay: {delay:.2f}s; }}')
        
    svg.append('.pulse { animation: p 2s infinite; }')
    svg.append('@keyframes p { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }')
    svg.append('</style>')
    
    # Terminal frame
    svg.append(f'<rect x="10" y="10" width="1160" height="590" fill="none" stroke="{chrome_color}" stroke-width="2"/>')
    svg.append(f'<rect x="10" y="10" width="1160" height="30" fill="{chrome_color}" opacity="0.1"/>')
    svg.append(f'<text x="25" y="30" fill="{chrome_color}" font-size="14" font-weight="bold">profile.sh --live</text>')
    
    # Portrait container
    svg.append(f'<rect x="40" y="60" width="340" height="380" fill="none" stroke="{chrome_color}" stroke-width="1" opacity="0.5"/>')
    svg.append(f'<text x="40" y="460" fill="{chrome_color}" font-size="12">VISUAL.MAP</text>')
    
    # Dots drawing
    svg.append('<g transform="translate(60, 80)">') # Center 300x340 in 340x380
    for i in range(num_groups):
        if paths_by_group[i]:
            path_data = " ".join(paths_by_group[i])
            svg.append(f'<path class="d g{i}" d="{path_data}"/>')
    svg.append('</g>')
    
    # Info panel
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
        ("Grid.Portfolio", "coming soon"),
        ("Grid.LinkedIn", "afnaan22mis1157"),
        ("Grid.GitHub", "22MIS1157")
    ]
    
    y_offset = 40
    for label, value in info_data:
        # We simulate dotted leaders. Total characters space = 65
        dots = "." * max(2, 65 - len(label) - len(value))
        
        svg.append(f'<text x="0" y="{y_offset}" fill="{chrome_color}" font-size="14">{label}</text>')
        svg.append(f'<text x="{len(label)*8 + 5}" y="{y_offset}" fill="{chrome_color}" font-size="14" opacity="0.3" textLength="{len(dots)*8}" lengthAdjust="spacingAndGlyphs">{dots}</text>')
        svg.append(f'<text x="520" y="{y_offset}" fill="{text_color}" font-size="14" text-anchor="end">{value}</text>')
        y_offset += 23
        
    svg.append('</g>')
    
    # Handle pill badge
    svg.append(f'<g transform="translate(420, 25)">')
    svg.append(f'<rect x="0" y="0" width="180" height="24" rx="12" fill="{accent_color}" opacity="0.9"/>')
    svg.append(f'<text x="90" y="16" fill="white" font-size="14" text-anchor="middle" font-weight="bold">@22MIS1157</text>')
    svg.append(f'</g>')

    # Footer note
    svg.append(f'<text x="40" y="580" fill="{chrome_color}" font-size="11" opacity="0.5">• More about me &amp; projects below in README ↓</text>')

    svg.append('</svg>')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(svg))
    print(f"Generated {output_path}")

def process_image(img_path, is_dark):
    img = Image.open(img_path).convert("RGBA")
    
    if is_dark:
        # Segment background out for dark mode
        img = remove(img)
    
    # White bg
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, (0, 0), img)
    img = bg.convert("L")
    
    # Crop to aspect ratio 300x340 -> 15:17
    w, h = img.size
    target_ratio = 300 / 340.0
    img_ratio = w / h
    
    if img_ratio > target_ratio:
        new_w = int(h * target_ratio)
        offset = (w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, h))
    else:
        new_h = int(w / target_ratio)
        offset = (h - new_h) // 2
        img = img.crop((0, offset, w, offset + new_h))
        
    img = img.resize((300, 340), Image.Resampling.LANCZOS)
    
    # AutoContrast cutoff 1
    img = ImageOps.autocontrast(img, cutoff=1)
    
    # Contrast 1.3x
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)
    
    # UnsharpMask radius=3, percent=140
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    
    if not is_dark:
        # For light mode, keep background, dots draw dark parts (which means we dither normally)
        pass
    else:
        # For dark mode, segment out, dots draw the lit subject, so invert?
        # Actually standard dither: 0=black dot, 255=white paper.
        # Dark mode: we want dots to draw the lit subject. Lit = bright.
        # So we invert the image before dithering so bright parts get more dots.
        img = ImageOps.invert(img)
        
    dot_matrix = floyd_steinberg_dither(img, serpentine=True)
    return dot_matrix

def main():
    img_path = r"C:\Users\Affu\.gemini\antigravity\brain\226fb60e-33bd-4628-ac5d-b326ef3d2cfb\media__1784382581810.jpg"
    
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
    
    output_dir = r"c:\Users\Affu\Downloads\22MIS1157"
    
    print("Generating Dark Mode SVG...")
    dark_dots = process_image(img_path, is_dark=True)
    generate_svg(dark_dots, palettes['dark'], True, os.path.join(output_dir, "dark.svg"))
    
    print("Generating Light Mode SVG...")
    light_dots = process_image(img_path, is_dark=False)
    generate_svg(light_dots, palettes['light'], False, os.path.join(output_dir, "light.svg"))

if __name__ == "__main__":
    main()
