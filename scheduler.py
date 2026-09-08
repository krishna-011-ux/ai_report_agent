"""
Scheduler
---------
This script automatically runs the pipeline according to a defined
schedule without requiring manual execution (daily/weekly/monthly).

Usage:
    python scheduler.py

For running continuously in production:
  - Run it as a background process (nohup / systemd service) on a VM/server, OR
  - Set up a cron job (Linux): crontab -e
        0 9 * * * cd /path/to/project && python main.py
  - On the cloud: AWS Lambda + EventBridge, or a GitHub Actions scheduled workflow
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
        print(
            "Scheduler is disabled in the configuration. "
            "Set schedule.enabled: true in config.yaml."
        )
        return

    frequency = sched_cfg.get("frequency", "daily")
    run_time = sched_cfg.get("time", "09:00")

    if frequency == "daily":
        schedule_lib.every().day.at(run_time).do(job)

    elif frequency == "weekly":
        schedule_lib.every().monday.at(run_time).do(job)

    elif frequency == "monthly":
        # The 'schedule' library does not support monthly scheduling,
        # so the job runs daily and executes only on the first day of the month.
        schedule_lib.every().day.at(run_time).do(
            lambda: job()
            if __import__("datetime").date.today().day == 1
            else None
        )

    print(
        f"Scheduler started: {frequency} at {run_time}. "
        "Press Ctrl+C to stop."
    )

    while True:
        schedule_lib.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    start_scheduler()
