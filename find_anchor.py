with open(r'C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'FALLBACK_JOBS' in line:
        print(f"Line {i+1}: {repr(line[:120])}")
    if i > 0 and 'FALLBACK_JOBS' in lines[i-1]:
        print(f"Line {i+1} (after): {repr(line[:120])}")
