"""
update_db.py  –  Synchronisiert jobs_dashboard.json + job_status.json → SQLite-DB
Wird vom daily Scheduled Task (SKILL.md Schritt G2) aufgerufen.
Gibt Statistiken aus fuer den Abschlussbericht.
"""
import sqlite3, json, os, sys
from datetime import date

DB_PATH          = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs.db"
JSON_JOBS        = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json"
JSON_STATUS      = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\job_status.json"

def make_key(j):
    t = (j.get("title","") or "").lower().strip()
    c = (j.get("company","") or "").lower().strip()
    return f"{t}|{c}"

def sync_jobs(conn):
    if not os.path.exists(JSON_JOBS):
        print("WARN: jobs_dashboard.json nicht gefunden"); return 0
    with open(JSON_JOBS,"r",encoding="utf-8") as f:
        jobs = json.load(f)

    new_count = 0
    for j in jobs:
        key = make_key(j)
        # INSERT OR IGNORE – neue Jobs kommen hinzu, bestehende bleiben unveraendert
        cur = conn.execute("""
            INSERT OR IGNORE INTO jobs
                (job_key,title,company,location,url,salary_text,salary_val,
                 source,score,pub_date,mail_date,date_added)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            key,
            j.get("title",""), j.get("company",""), j.get("location",""),
            j.get("url",""), j.get("salary_text",""),
            float(j.get("salary_val",0) or 0),
            j.get("source",""), int(j.get("score",0) or 0),
            j.get("pub_date",""),
            j.get("mail_date","") or j.get("date_added",""),
            j.get("date_added",""),
        ))
        if cur.rowcount > 0:
            new_count += 1
    conn.commit()
    return new_count

def sync_status(conn):
    if not os.path.exists(JSON_STATUS):
        return 0  # noch keine Statusdaten
    with open(JSON_STATUS,"r",encoding="utf-8") as f:
        raw = json.load(f)

    # raw hat Eintraege wie: {"title|company": "starred", "title|company_date": "2026-05-21"}
    synced = 0
    today = date.today().isoformat()
    keys_done = set()
    for k, v in raw.items():
        if k.endswith("_date"):
            continue  # wird zusammen mit dem Haupt-Key verarbeitet
        if k in keys_done:
            continue
        keys_done.add(k)
        status     = v
        apply_date = raw.get(k + "_date", "")
        conn.execute("""
            INSERT INTO job_status (job_key, status, status_date, applied_at)
            VALUES (?,?,?,?)
            ON CONFLICT(job_key) DO UPDATE SET
                status     = excluded.status,
                status_date = excluded.status_date,
                applied_at  = CASE WHEN excluded.applied_at != '' THEN excluded.applied_at
                                   ELSE job_status.applied_at END
        """, (k, status, today, apply_date))
        synced += 1
    conn.commit()
    return synced

def record_daily_run(conn, new_jobs):
    today = date.today().isoformat()
    total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    top   = conn.execute("SELECT MAX(score) FROM jobs WHERE date_added=?", (today,)).fetchone()[0] or 0
    srcs  = conn.execute(
        "SELECT GROUP_CONCAT(DISTINCT source) FROM jobs WHERE date_added=?", (today,)
    ).fetchone()[0] or ""
    conn.execute("""
        INSERT INTO daily_runs (run_date,new_jobs,total_jobs,sources_hit,top_score)
        VALUES (?,?,?,?,?)
        ON CONFLICT(run_date) DO UPDATE SET
            new_jobs   = excluded.new_jobs,
            total_jobs = excluded.total_jobs,
            sources_hit= excluded.sources_hit,
            top_score  = excluded.top_score
    """, (today, new_jobs, total, srcs, top))
    conn.commit()
    return total, top

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")

    new_jobs  = sync_jobs(conn)
    synced_st = sync_status(conn)
    total, top = record_daily_run(conn, new_jobs)

    # Ausgabe fuer Abschlussbericht
    print(f"DB_UPDATE: new={new_jobs} total={total} top_score={top} status_synced={synced_st}")

    conn.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
