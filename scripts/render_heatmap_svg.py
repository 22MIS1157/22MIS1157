import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BG = "#0d1117"
FG = "#c9d1d9"
MUTED = "#8b949e"
FONT = "monospace"

BOX = 13
GAP = 3
STRIDE = BOX + GAP
RADIUS = 2
MARGIN_LEFT = 40
MARGIN_TOP = 50

DAY_LABELS = ["Mon", "", "Wed", "", "Fri", "", ""]
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def main():
    data_path = ROOT / "data" / "contributions.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    days = data["days"]
    
    if not days:
        print("[heatmap] No data found")
        return
    
    date_map = {d["date"]: d["level"] for d in days}
    
    today = datetime.now()
    start = today - timedelta(days=today.weekday() + 1)
    start = start - timedelta(weeks=52)
    
    weeks = []
    current = start
    week = []
    while current <= today:
        date_str = current.strftime("%Y-%m-%d")
        level = date_map.get(date_str, 0)
        level = min(level, len(PALETTE) - 1)
        week.append((date_str, level, current.weekday()))
        if current.weekday() == 6:
            weeks.append(week)
            week = []
        current += timedelta(days=1)
    if week:
        weeks.append(week)
    
    num_weeks = len(weeks)
    grid_w = num_weeks * STRIDE
    grid_h = 7 * STRIDE
    W = MARGIN_LEFT + grid_w + 40
    stats_h = 50
    legend_h = 30
    H = MARGIN_TOP + grid_h + legend_h + stats_h + 20
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    svg.append(f'<rect width="100%" height="100%" rx="12" fill="{BG}"/>')
    svg.append(f'<rect width="100%" height="100%" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>')
    
    total = data.get("total_contributions", 0)
    svg.append(f'<text x="{MARGIN_LEFT}" y="25" font-family="{FONT}" font-size="14" fill="{FG}" font-weight="bold">{total:,} contributions in the last year</text>')
    
    month_positions = {}
    for wi, week in enumerate(weeks):
        if week:
            d = datetime.strptime(week[0][0], "%Y-%m-%d")
            month = d.month
            if month not in month_positions:
                month_positions[month] = wi
    
    for month, wi in month_positions.items():
        x = MARGIN_LEFT + wi * STRIDE
        svg.append(f'<text x="{x}" y="{MARGIN_TOP - 8}" font-family="{FONT}" font-size="11" fill="{MUTED}">{MONTH_NAMES[month - 1]}</text>')
    
    for i, label in enumerate(DAY_LABELS):
        if label:
            y = MARGIN_TOP + i * STRIDE + BOX - 2
            svg.append(f'<text x="{MARGIN_LEFT - 30}" y="{y}" font-family="{FONT}" font-size="11" fill="{MUTED}">{label}</text>')
    
    svg.append('<style>')
    svg.append('  @keyframes slide-in { 0% { opacity:0; transform:scale(0) } 100% { opacity:1; transform:scale(1) } }')
    svg.append('</style>')
    
    for wi, week in enumerate(weeks):
        for day_data in week:
            date_str, level, weekday = day_data
            x = MARGIN_LEFT + wi * STRIDE
            y = MARGIN_TOP + weekday * STRIDE
            color = PALETTE[level]
            delay = (wi + weekday) * 0.012
            svg.append(f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="{RADIUS}" fill="{color}" style="animation: slide-in 0.3s {delay:.3f}s ease forwards; opacity:0; transform-origin:{x + BOX//2}px {y + BOX//2}px;"/>')
    
    legend_y = MARGIN_TOP + grid_h + 15
    svg.append(f'<text x="{W - 180}" y="{legend_y + 10}" font-family="{FONT}" font-size="11" fill="{MUTED}">Less</text>')
    for i, c in enumerate(PALETTE):
        lx = W - 150 + i * (BOX + 3)
        svg.append(f'<rect x="{lx}" y="{legend_y}" width="{BOX}" height="{BOX}" rx="{RADIUS}" fill="{c}"/>')
    svg.append(f'<text x="{W - 150 + len(PALETTE) * (BOX + 3) + 5}" y="{legend_y + 10}" font-family="{FONT}" font-size="11" fill="{MUTED}">More</text>')
    
    stats_y = legend_y + 35
    streak = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    best = data.get("best_day", {})
    svg.append(f'<text x="{MARGIN_LEFT}" y="{stats_y}" font-family="{FONT}" font-size="12" fill="{MUTED}">')
    svg.append(f'  Current Streak: <tspan fill="{FG}" font-weight="bold">{streak} days</tspan>')
    svg.append(f'  &#160;&#160;|&#160;&#160; Longest: <tspan fill="{FG}" font-weight="bold">{longest} days</tspan>')
    svg.append(f'  &#160;&#160;|&#160;&#160; Best Day: <tspan fill="{FG}" font-weight="bold">{best.get("count", 0)} contributions</tspan>')
    svg.append(f'</text>')
    
    svg.append('</svg>')
    
    out = ROOT / "contrib-heatmap.svg"
    out.write_text('\n'.join(svg), encoding='utf-8')
    print(f"[heatmap] Written {out} ({num_weeks} weeks)")

if __name__ == "__main__":
    main()
