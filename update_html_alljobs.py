# -*- coding: utf-8 -*-
import io, json, re
H = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\index.html"
P = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json"
with io.open(P, encoding="utf-8") as f:
    db = json.load(f)
with io.open(H, encoding="utf-8") as f:
    t = f.read()
t = re.sub(r"const TODAY = '[^']*'", "const TODAY = '2026-06-12'", t)
start = t.index("const ALL_JOBS = [")
end = t.index("];", start) + 2
arr = ",\n".join(json.dumps(j, ensure_ascii=False) for j in db)
t = t[:start] + "const ALL_JOBS = [\n" + arr + "\n];" + t[end:]
with io.open(H, "w", encoding="utf-8") as f:
    f.write(t)
print("OK: ALL_JOBS=%d TODAY=2026-06-12" % len(db))
