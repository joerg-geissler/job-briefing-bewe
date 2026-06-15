p = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\index.html"
lines = open(p, encoding="utf-8").read().splitlines()
for i, l in enumerate(lines):
    if "FALLBACK_JOBS" in l:
        for j in range(i, min(i+6, len(lines))):
            print(j+1, "|", lines[j][:200])
        break
