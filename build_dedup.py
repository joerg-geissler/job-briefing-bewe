import json
with open(r'C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)
dedup = set()
for j in jobs:
    key = (j.get('company','') + '|' + j.get('title','') + '|' + j.get('location','')).lower()
    dedup.add(key)
print(f'DEDUP_COUNT: {len(dedup)}')
print(f'TOTAL_JOBS: {len(jobs)}')
