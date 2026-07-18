"""
Script to generate real backdated Git commits from January 1st, 2026 to today.
This updates your actual GitHub contribution calendar on your profile.
"""
import subprocess
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY_FILE = ROOT / "data" / "history.txt"

def run_git(args, env=None):
    subprocess.run(["git"] + args, cwd=str(ROOT), check=True, capture_output=True, env=env)

def main():
    # Define start and end date
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()
    
    current_date = start_date
    total_commits = 0
    
    print("[commits] Generating active Git history from Jan 1, 2026 to today...")
    
    # Ensure history file and directory exist
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    while current_date <= end_date:
        # Seed with date so it is deterministic if run multiple times
        # (Though we'll only run this once to generate the commits)
        date_str = current_date.strftime("%Y-%m-%d")
        rnd = random.Random(date_str + "real_activity")
        
        # 70% chance of contributing on any given day
        if rnd.random() < 0.70:
            # 1 to 5 commits per day
            num_commits = rnd.randint(1, 5)
            for i in range(num_commits):
                # Add variation to commit time
                hour = rnd.randint(9, 21)
                minute = rnd.randint(0, 59)
                second = rnd.randint(0, 59)
                commit_time = f"{date_str} {hour:02d}:{minute:02d}:{second:02d}"
                
                # Append to history file to make a unique file change
                with open(HISTORY_FILE, "a") as f:
                    f.write(f"Contribution entry on {commit_time}\n")
                
                # Stage history file
                run_git(["add", "data/history.txt"])
                
                # Set both author and committer dates to make sure GitHub registers it correctly
                env = {
                    "GIT_AUTHOR_DATE": f"{commit_time} +0530",
                    "GIT_COMMITTER_DATE": f"{commit_time} +0530"
                }
                
                # Commit
                run_git([
                    "commit", 
                    "-m", f"chore: update neural logs for {date_str} (part {i+1})"
                ], env=env)
                
                total_commits += 1
                
        current_date += timedelta(days=1)
        
    print(f"[commits] Successfully created {total_commits} backdated commits locally!")

if __name__ == "__main__":
    main()
