"""
Scheduler
---------
Ye script pipeline ko automatically, bina manual run kiye, schedule
ke hisaab se chalata rehta hai (daily/weekly/monthly).

Usage:
    python scheduler.py

Isko production mein 24/7 chalane ke liye:
  - Ek chhoti VM/server pe background process (nohup / systemd service) ki tarah chalao, YA
  - Cron job set kar do (Linux): crontab -e
        0 9 * * * cd /path/to/project && python main.py
  - Cloud pe: AWS Lambda + EventBridge, ya GitHub Actions scheduled workflow
"""

import time
import schedule as schedule_lib

from main import load_config, run_pipeline


def job():
    config = load_config("config/config.yaml")
    run_pipeline(config)


def start_scheduler():
    config = load_config("config/config.yaml")
    sched_cfg = config.get("schedule", {})

    if not sched_cfg.get("enabled", False):
        print("Scheduler config mein disabled hai. config.yaml mein schedule.enabled: true karo.")
        return

    frequency = sched_cfg.get("frequency", "daily")
    run_time = sched_cfg.get("time", "09:00")

    if frequency == "daily":
        schedule_lib.every().day.at(run_time).do(job)
    elif frequency == "weekly":
        schedule_lib.every().monday.at(run_time).do(job)
    elif frequency == "monthly":
        # 'schedule' library monthly support nahi karti, isliye har din check karke
        # month ka 1st din run karte hain
        schedule_lib.every().day.at(run_time).do(
            lambda: job() if __import__("datetime").date.today().day == 1 else None
        )

    print(f"Scheduler shuru ho gaya: {frequency} at {run_time}. Ctrl+C se rokein.")
    while True:
        schedule_lib.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    start_scheduler()
