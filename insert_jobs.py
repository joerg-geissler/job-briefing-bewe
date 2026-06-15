#!/usr/bin/env python3
import json

db_path = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json"
new_path = r"C:\Users\joerg\job-briefing-public\new_jobs.json"

with open(db_path, 'r', encoding='utf-8') as f:
    existing = json.load(f)

with open(new_path, 'r', encoding='utf-8') as f:
    new_jobs = json.load(f)

combined = new_jobs + existing

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(combined, f, ensure_ascii=False, indent=4)

print(f"DB updated: {len(new_jobs)} new + {len(existing)} existing = {len(combined)} total")
