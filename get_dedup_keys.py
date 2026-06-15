import json
data = json.load(open(r'C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json', encoding='utf-8'))
keys = [(d.get('company','')+'|'+d.get('title','')+'|'+d.get('location','')).lower() for d in data]
print(json.dumps(keys))
print('TOTAL:', len(data))
