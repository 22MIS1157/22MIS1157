import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
USERNAME = "22MIS1157"

def main():
    url = f"https://github.com/users/{USERNAME}/contributions"
    print(f"[fetch] GET {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    days = []
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        cells = soup.select("[data-date]")
    
    for cell in cells:
        date_str = cell.get("data-date", "")
        level = int(cell.get("data-level", 0))
        count = 0
        label = cell.get("aria-label", "")
        if label:
            parts = label.split(" ")
            if parts and parts[0].isdigit():
                count = int(parts[0])
        if date_str:
            days.append({"date": date_str, "count": count, "level": level})
    
    days.sort(key=lambda d: d["date"])


    
    total = sum(d["count"] for d in days)
    best_day = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}
    
    current_streak = 0
    today = datetime.now().strftime("%Y-%m-%d")
    for d in reversed(days):
        if d["date"] > today:
            continue
        if d["count"] > 0:
            current_streak += 1
        else:
            break
    
    longest_streak = 0
    streak = 0
    for d in days:
        if d["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0
    
    monthly = defaultdict(int)
    for d in days:
        if d["date"]:
            monthly[d["date"][:7]] += d["count"]
    
    data = {
        "username": USERNAME,
        "generated_at": datetime.now().isoformat(),
        "total_contributions": total,
        "best_day": {"date": best_day["date"], "count": best_day["count"]},
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "monthly": dict(monthly),
        "days": days
    }
    
    out_path = ROOT / "data" / "contributions.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[fetch] Saved {len(days)} days, {total} total contributions to {out_path}")

if __name__ == "__main__":
    main()
