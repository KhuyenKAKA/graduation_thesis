"""
Scheduled jobs for periodic data sync.

Schedule: 1st of every month at 02:00 AM
  - crawl_universities_job : updates raw_data_visualize_1.json with latest rankings
  - clean_entry_infor_job  : parses university_texts → re-populates entry_infor table
  - crawl_majors_job       : upserts university↔major mappings in DB
"""

import json
import logging
import re
import time
from enum import Enum
from pathlib import Path

import cloudscraper
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import text

from app.database import SessionLocal

logger = logging.getLogger(__name__)

# ── Path to the JSON data file (project_root/data/raw_data_visualize_1.json) ──
_PROJECT_ROOT = Path(__file__).parents[3]  # backend/app/utils → backend/app → backend → project root
_JSON_DATA_FILE = _PROJECT_ROOT / "data" / "raw_data_visualize_1.json"

BASE_URL = (
    "https://www.topuniversities.com/rankings/endpoint"
    "?nid=4114613&page={page}&items_per_page=150&tab=indicators"
    "&region=&countries=&cities=&search=&star=&sort_by=&order_by="
    "&program_type=&scholarship=&fee=&english_score=&academic_score="
    "&mix_student=&loggedincache=7047458-1778000320765&study_level=&subjects="
)

MAJORS = [
    "Engineering - Chemical",
    "Engineering - Civil and Structural",
    "Computer Science and Information Systems",
    "Data Science and Artificial Intelligence",
    "Engineering - Electrical and Electronic",
    "Engineering - Petroleum",
    "Engineering - Mechanical",
    "Engineering - Mineral and Mining",
]


# ── Job 1: Crawl raw university rankings → JSON ───────────────────────────────

def crawl_universities_job():
    """Fetch latest university rankings from TopUniversities and update local JSON."""
    logger.info("[Scheduler] crawl_universities_job started.")

    if not _JSON_DATA_FILE.exists():
        logger.warning(f"[Scheduler] JSON file not found: {_JSON_DATA_FILE}. Starting with empty list.")
        existing_data = []
    else:
        with open(_JSON_DATA_FILE, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                logger.error("[Scheduler] JSON file is corrupted. Aborting crawl_universities_job.")
                return

    scraper = cloudscraper.create_scraper()
    new_entries = []

    for page in range(4):
        url = BASE_URL.format(page=page)
        try:
            resp = scraper.get(url, timeout=30)
            resp.raise_for_status()
            nodes = resp.json().get("score_nodes", [])
        except Exception as e:
            logger.warning(f"[Scheduler] Page {page} failed: {e}")
            continue

        for node in nodes:
            entry = {
                "score_nid":    node.get("score_nid"),
                "nid":          node.get("nid"),
                "core_id":      node.get("core_id"),
                "title":        node.get("title"),
                "path":         node.get("path"),
                "region":       node.get("region"),
                "country":      node.get("country"),
                "city":         node.get("city"),
                "logo":         node.get("logo"),
                "overall_score": node.get("overall_score"),
                "rank_display": node.get("rank_display"),
                "rank":         node.get("rank"),
                "more_info":    node.get("more_info"),
                "scores":       node.get("scores"),
            }
            new_entries.append(entry)

        time.sleep(0.5)

    if new_entries:
        existing_data.extend(new_entries)
        with open(_JSON_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
        logger.info(f"[Scheduler] crawl_universities_job done. Added {len(new_entries)} entries → {_JSON_DATA_FILE}")
    else:
        logger.warning("[Scheduler] crawl_universities_job: no data fetched, JSON not updated.")

    # Sau khi crawl xong, chạy clean để cập nhật entry_infor
    clean_entry_infor_job()


# ── Job 2: Clean university_texts → entry_infor ─────────────────────────────

class _TypeDegree(Enum):
    Bachelor = 1
    Master = 2


def _parse_entry_requirements(value: str) -> tuple:
    """Parse university_information text into Bachelor/Master requirement dicts."""
    requirement_keys = ["SAT", "GRE", "GMAT", "ACT", "ATAR", "GPA", "TOEFL", "IELTS"]
    empty = lambda: {k: None for k in requirement_keys}

    Bachelor_req = empty()
    Master_req = empty()
    haveBachelor = False
    haveMaster = False

    master_parts = [x.strip() for x in value.split("Master") if "+" in x]
    if len(master_parts) > 1:
        tokens = master_parts[1].strip().split()
        for i in range(len(tokens) - 1):
            if tokens[i] in requirement_keys and any(c.isdigit() for c in tokens[i + 1]):
                haveMaster = True
                Master_req[tokens[i]] = tokens[i + 1]

    bachelor_raw = value.split("Master")[0].strip()
    bachelor_parts = [
        x.strip()
        for first in bachelor_raw.split("Bachelor")
        for x in first.split("General")
        if "+" in x and "email" not in x
    ]
    if bachelor_parts:
        tokens = bachelor_parts[0].split()
        for i in range(len(tokens) - 1):
            if tokens[i] in requirement_keys and any(c.isdigit() for c in tokens[i + 1]):
                haveBachelor = True
                Bachelor_req[tokens[i]] = tokens[i + 1]

    return haveBachelor, Bachelor_req, haveMaster, Master_req


def clean_entry_infor_job():
    """Parse university_texts and re-populate the entry_infor table."""
    logger.info("[Scheduler] clean_entry_infor_job started.")
    db = SessionLocal()
    try:
        db.execute(text("DROP TABLE IF EXISTS entry_infor"))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS entry_infor (
                id            INT AUTO_INCREMENT PRIMARY KEY,
                university_id INT,
                degree_type   INT,
                SAT           VARCHAR(20),
                GRE           VARCHAR(20),
                GMAT          VARCHAR(20),
                ACT           VARCHAR(20),
                ATAR          VARCHAR(20),
                GPA           VARCHAR(20),
                TOEFL         VARCHAR(20),
                IELTS         VARCHAR(20),
                FOREIGN KEY (university_id) REFERENCES universities(id)
            )
        """))
        db.commit()

        rows = db.execute(text("SELECT id, university_information FROM university_texts")).fetchall()
        inserted = 0

        for uni_id, info_text in rows:
            if not info_text:
                continue
            haveBachelor, b_req, haveMaster, m_req = _parse_entry_requirements(info_text)

            if haveBachelor:
                db.execute(text("""
                    INSERT INTO entry_infor
                        (university_id, degree_type, SAT, GRE, GMAT, ACT, ATAR, GPA, TOEFL, IELTS)
                    VALUES
                        (:uid, :deg, :sat, :gre, :gmat, :act, :atar, :gpa, :toefl, :ielts)
                """), {"uid": uni_id, "deg": _TypeDegree.Bachelor.value, **{k.lower(): v for k, v in b_req.items()}})
                inserted += 1

            if haveMaster:
                db.execute(text("""
                    INSERT INTO entry_infor
                        (university_id, degree_type, SAT, GRE, GMAT, ACT, ATAR, GPA, TOEFL, IELTS)
                    VALUES
                        (:uid, :deg, :sat, :gre, :gmat, :act, :atar, :gpa, :toefl, :ielts)
                """), {"uid": uni_id, "deg": _TypeDegree.Master.value, **{k.lower(): v for k, v in m_req.items()}})
                inserted += 1

        db.commit()
        logger.info(f"[Scheduler] clean_entry_infor_job done. Inserted {inserted} rows into entry_infor.")
    except Exception as e:
        logger.error(f"[Scheduler] clean_entry_infor_job failed: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


# ── Job 3: Crawl university↔major mappings → DB ───────────────────────────────

def crawl_majors_job():
    """Fetch university major data and upsert university_majors in DB."""
    logger.info("[Scheduler] crawl_majors_job started.")
    db = SessionLocal()
    try:
        # Ensure tables exist
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS majors (
                id   INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS university_majors (
                id            INT AUTO_INCREMENT PRIMARY KEY,
                university_id INT NOT NULL,
                major_id      INT NOT NULL,
                UNIQUE KEY uq_uni_major (university_id, major_id),
                FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
                FOREIGN KEY (major_id)      REFERENCES majors(id)       ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        db.commit()

        # Upsert majors, collect id map
        major_id_map: dict[str, int] = {}
        for name in MAJORS:
            db.execute(
                text("INSERT INTO majors (name) VALUES (:name) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)"),
                {"name": name},
            )
            db.commit()
            row = db.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
            major_id_map[name] = row[0]

        scraper = cloudscraper.create_scraper()
        total_linked = 0
        total_not_found: list[str] = []

        for page in range(4):
            url = BASE_URL.format(page=page)
            try:
                resp = scraper.get(url, timeout=30)
                resp.raise_for_status()
                nodes = resp.json().get("score_nodes", [])
            except Exception as e:
                logger.warning(f"[Scheduler] Page {page} failed: {e}")
                continue

            for node in nodes:
                title = node.get("title", "").strip()
                if not title:
                    continue

                row = db.execute(
                    text("SELECT id FROM universities WHERE name = :name LIMIT 1"),
                    {"name": title},
                ).fetchone()
                if not row:
                    row = db.execute(
                        text("SELECT id FROM universities WHERE name LIKE :name LIMIT 1"),
                        {"name": f"%{title[:40]}%"},
                    ).fetchone()
                if not row:
                    total_not_found.append(title)
                    continue

                uni_id = row[0]
                for major_id in major_id_map.values():
                    db.execute(
                        text("INSERT IGNORE INTO university_majors (university_id, major_id) VALUES (:uid, :mid)"),
                        {"uid": uni_id, "mid": major_id},
                    )
                total_linked += 1

            db.commit()
            time.sleep(0.5)

        logger.info(
            f"[Scheduler] crawl_majors_job done. "
            f"Linked {total_linked} universities × {len(major_id_map)} majors. "
            f"Not found: {len(total_not_found)}."
        )
        if total_not_found:
            logger.debug(f"[Scheduler] Not found: {total_not_found[:10]} ...")

    except Exception as e:
        logger.error(f"[Scheduler] crawl_majors_job failed: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def create_scheduler() -> BackgroundScheduler:
    """Create and configure the APScheduler instance with all jobs."""
    scheduler = BackgroundScheduler()

    # Run both jobs on the 1st of every month at 02:00 AM
    monthly_trigger = CronTrigger(day=1, hour=2, minute=0)

    scheduler.add_job(
        crawl_universities_job,
        trigger=monthly_trigger,
        id="crawl_universities",
        replace_existing=True,
    )
    scheduler.add_job(
        crawl_majors_job,
        trigger=CronTrigger(day=1, hour=2, minute=30),  # 30 min after universities job
        id="crawl_majors",
        replace_existing=True,
    )

    logger.info("[Scheduler] Jobs registered: crawl_universities (day=1 02:00), crawl_majors (day=1 02:30)")
    return scheduler
