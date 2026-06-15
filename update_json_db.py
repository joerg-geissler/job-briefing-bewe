import json

# Load new jobs
with open(r'C:\Users\joerg\job-briefing-public\new_jobs.json', 'r', encoding='utf-8') as f:
    new_jobs = json.load(f)

# Load existing DB
db_path = r'C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json'
with open(db_path, 'r', encoding='utf-8') as f:
    existing_jobs = json.load(f)

# Prepend new jobs
updated = new_jobs + existing_jobs

# Write back
with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(updated, f, ensure_ascii=False, indent=4)

print(f"JSON_DB: new={len(new_jobs)} total={len(updated)}")
