"""
Standalone script to run the scheduler.

Usage:
    # Normal mode - jobs run on schedule (1st of every month)
    python run_scheduler.py

    # Test mode - jobs fire immediately (set TEST_MODE = True below)
    python run_scheduler.py
"""

import logging
import time
import sys
import os

# ── Add backend/ to path so `app` package is importable ──────────────────────
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("run_scheduler")

# ── Config ────────────────────────────────────────────────────────────────────

# Set True để jobs chạy ngay lập tức (dùng để test)
# Set False để chạy theo đúng lịch (mùng 1 mỗi tháng)
TEST_MODE = True

# Khi TEST_MODE=True, script tự thoát sau N giây (đủ để job hoàn thành)
TEST_TIMEOUT_SECONDS = 120

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import datetime
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from app.utils.scheduler import crawl_universities_job, crawl_majors_job

    scheduler = BackgroundScheduler()

    if TEST_MODE:
        scheduler.add_job(
            crawl_majors_job,
            trigger=CronTrigger(day=1, hour=2, minute=30),
            id="crawl_majors",
            next_run_time=datetime.now(),
        )
    else:
        logger.info("=== PRODUCTION MODE: jobs run on 1st of every month ===")
        from app.utils.scheduler import create_scheduler
        scheduler = create_scheduler()

    scheduler.start()
    logger.info(f"Scheduler started. Jobs: {[j.id for j in scheduler.get_jobs()]}")

    try:
        if TEST_MODE:
            logger.info(f"Waiting {TEST_TIMEOUT_SECONDS}s for jobs to complete...")
            time.sleep(TEST_TIMEOUT_SECONDS)
            logger.info("Test timeout reached, shutting down.")
        else:
            logger.info("Running indefinitely. Press Ctrl+C to stop.")
            while True:
                time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped.")
