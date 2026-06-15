with open(r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\index.html", encoding="utf-8") as f:
    content = f.read()
idx = content.find("const FALLBACK_JOBS = [")
print("Found at char:", idx)
print(repr(content[idx:idx+400]))
