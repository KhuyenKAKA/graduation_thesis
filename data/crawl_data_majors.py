import cloudscraper
import mysql.connector
import time

# ── DB connection ─────────────────────────────────────────
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@Khuyen2903",
    database="universities_db"
)
cursor = conn.cursor()

# ── Step 1: Create tables if not exist ───────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS majors (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS university_majors (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    university_id INT NOT NULL,
    major_id      INT NOT NULL,
    UNIQUE KEY uq_uni_major (university_id, major_id),
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    FOREIGN KEY (major_id)      REFERENCES majors(id)       ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")
conn.commit()
print("[OK] Tables ensured.")

# ── Step 2: Insert majors from the subjects list ──────────
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

major_id_map = {}  # name -> id

for name in MAJORS:
    cursor.execute(
        "INSERT INTO majors (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
        (name,)
    )
    conn.commit()
    major_id_map[name] = cursor.lastrowid

print(f"[OK] Inserted/resolved {len(major_id_map)} majors:")
for name, mid in major_id_map.items():
    print(f"     [{mid}] {name}")

# ── Step 3: Crawl API (4 pages) and link universities ─────
BASE_URL = (
    "https://www.topuniversities.com/rankings/endpoint"
    "?nid=4114613&page={page}&items_per_page=150&tab=indicators"
    "&region=&countries=&cities=&search=&star=&sort_by=&order_by="
    "&program_type=&scholarship=&fee=&english_score=&academic_score="
    "&mix_student=&loggedincache=7047458-1778000320765&study_level=&subjects="
)

scraper = cloudscraper.create_scraper()

total_linked = 0
total_not_found = []

for page in range(4):
    url = BASE_URL.format(page=page)
    print(f"\n[API] Fetching page {page}...")

    try:
        response = scraper.get(url, timeout=30)
        response.raise_for_status()
        raw = response.json()
    except Exception as e:
        print(f"     ERROR: {e}")
        continue

    nodes = raw.get("score_nodes", [])
    print(f"     Got {len(nodes)} universities.")

    for node in nodes:
        title = node.get("title", "").strip()
        if not title:
            continue

        # Find university in DB by exact name match
        cursor.execute(
            "SELECT id FROM universities WHERE name = %s LIMIT 1",
            (title,)
        )
        row = cursor.fetchone()

        if not row:
            # Try partial match (some names may differ slightly)
            cursor.execute(
                "SELECT id FROM universities WHERE name LIKE %s LIMIT 1",
                (f"%{title[:40]}%",)
            )
            row = cursor.fetchone()

        if not row:
            total_not_found.append(title)
            continue

        uni_id = row[0]

        # Fetch matched name from DB for verification
        cursor.execute("SELECT name FROM universities WHERE id = %s", (uni_id,))
        db_name = cursor.fetchone()[0]
        match_type = "EXACT" if db_name == title else "PARTIAL"
        print(f"     [{match_type}] API: '{title}' → DB: '{db_name}' (id={uni_id})")

        # Insert all majors for this university
        for major_id in major_id_map.values():
            cursor.execute(
                """
                INSERT IGNORE INTO university_majors (university_id, major_id, title)
                VALUES (%s, %s, %s)
                """,
                (uni_id, major_id, title)
            )
        total_linked += 1

    conn.commit()
    time.sleep(0.5)  # polite delay between pages

# ── Summary ───────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"[DONE] Linked {total_linked} universities × {len(major_id_map)} majors each.")
print(f"[DONE] Total university_majors rows inserted: {total_linked * len(major_id_map)}")

if total_not_found:
    print(f"\n[WARN] {len(total_not_found)} universities NOT found in DB:")
    for name in total_not_found[:20]:
        print(f"     - {name}")
    if len(total_not_found) > 20:
        print(f"     ... and {len(total_not_found) - 20} more.")

cursor.close()
conn.close()
