import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BG = "#0d1117"
FG = "#c9d1d9"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
YELLOW = "#d29922"
RED = "#f85149"
CYAN = "#39d353"
PURPLE = "#bc8cff"
ORANGE = "#f0883e"
FONT = "monospace"
FS = 14
LH = 22
STATIC = os.environ.get("STATIC", "0") == "1"

def main():
    info = [
        ("Name",  "Afnaan Ahmed P",                                      CYAN),
        ("Role",  "AI/ML Engineer • Backend Developer",                  GREEN),
        ("Univ",  "VIT Chennai — MTech Integrated, SE (2022-27)",        FG),
        ("CGPA",  "7.92 / 10.0 | 66 Subjects | No Backlogs",           FG),
        ("",      "",                                                     FG),
        ("Now",   "Research Intern @ CHAIR, VIT Chennai",                GREEN),
        ("Prev",  "Core Member, Cybersecurity Div @ MIC",                FG),
        ("",      "",                                                     FG),
        ("Lang",  "Python • JS • TS • Go • Java • C",                   ACCENT),
        ("AI/ML", "PyTorch • TensorFlow • YOLOv8 • OpenCV",             ACCENT),
        ("GenAI", "LangChain • LLaMA-3 • Gemini • RAG",                 PURPLE),
        ("Back",  "FastAPI • Node.js • Express • WebSocket",             ORANGE),
        ("Cloud", "AWS Lambda • S3 • DynamoDB • Docker • K8s",           YELLOW),
        ("DB",    "PostgreSQL • MongoDB • Redis • Supabase",             RED),
        ("",      "",                                                     FG),
        ("Proj1", "AI Anemia Detection — 96% acc, AUC 0.98",            GREEN),
        ("Proj2", "ICU Mortality Predictor — 96% AUC-ROC",              GREEN),
        ("Proj3", "ATCC VPark — IoT + YOLOv8 + Arduino",               GREEN),
        ("Proj4", "LexCloud — AWS Serverless + LLaMA-3 RAG",            GREEN),
    ]

    palette_colors = ["#f85149", "#f0883e", "#d29922", "#3fb950",
                      "#58a6ff", "#bc8cff", "#ff7b72", "#79c0ff"]

    W = 490
    header_h = 35
    content_start = header_h + 15
    visible_lines = sum(1 for l, v, _ in info if l or v)
    total_lines = len(info)
    palette_row_h = 30
    H = content_start + total_lines * LH + palette_row_h + 20

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    svg.append(f'<rect width="100%" height="100%" rx="12" fill="{BG}"/>')

    # Terminal title bar
    svg.append(f'<rect width="100%" height="{header_h}" rx="12" fill="#161b22"/>')
    svg.append(f'<rect y="{header_h - 8}" width="100%" height="8" fill="#161b22"/>')
    svg.append(f'<circle cx="20" cy="17" r="6" fill="{RED}"/>')
    svg.append(f'<circle cx="38" cy="17" r="6" fill="{YELLOW}"/>')
    svg.append(f'<circle cx="56" cy="17" r="6" fill="{GREEN}"/>')
    svg.append(f'<text x="{W // 2}" y="22" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{FG}" opacity="0.6">afnaan@github — neofetch</text>')

    # Border
    svg.append(f'<rect width="100%" height="100%" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>')

    if not STATIC:
        svg.append('<style>')
        for i in range(total_lines + 1):
            svg.append(f'  @keyframes fade-in-{i} {{ 0% {{ opacity:0; transform:translateX(-10px) }} 100% {{ opacity:1; transform:translateX(0) }} }}')
        svg.append('</style>')

    line_idx = 0
    for label, value, color in info:
        y = content_start + line_idx * LH + 14
        delay = 0.3 + line_idx * 0.08
        anim = f'animation: fade-in-{line_idx} 0.3s {delay}s ease forwards; opacity: 0;' if not STATIC else ''

        if not label and not value:
            line_idx += 1
            continue

        svg.append(f'<g style="{anim}">')
        if label:
            svg.append(f'  <text x="20" y="{y}" font-family="{FONT}" font-size="{FS}" fill="{ACCENT}" font-weight="bold">{label}</text>')
            svg.append(f'  <text x="80" y="{y}" font-family="{FONT}" font-size="{FS}" fill="#8b949e">~</text>')
            svg.append(f'  <text x="95" y="{y}" font-family="{FONT}" font-size="{FS}" fill="{color}">{value}</text>')
        svg.append('</g>')
        line_idx += 1

    # Color palette row
    palette_y = content_start + total_lines * LH + 5
    palette_delay = 0.3 + total_lines * 0.08
    anim = f'animation: fade-in-{total_lines} 0.3s {palette_delay}s ease forwards; opacity: 0;' if not STATIC else ''
    svg.append(f'<g style="{anim}">')
    block_w = 22
    start_x = 20
    for j, pc in enumerate(palette_colors):
        svg.append(f'  <rect x="{start_x + j * (block_w + 6)}" y="{palette_y}" width="{block_w}" height="{block_w}" rx="4" fill="{pc}"/>')
    svg.append('</g>')

    svg.append('</svg>')

    out = ROOT / "info-card.svg"
    out.write_text('\n'.join(svg), encoding='utf-8')
    print(f"[info-card] Written {out}")

if __name__ == "__main__":
    main()
