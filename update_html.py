#!/usr/bin/env python3
import json, re

html_path = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\index.html"
new_path = r"C:\Users\joerg\job-briefing-public\new_jobs.json"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

with open(new_path, 'r', encoding='utf-8') as f:
    new_jobs = json.load(f)

# Find the FALLBACK_JOBS section
pattern = r'(const FALLBACK_JOBS = \[)(.*?)(\];)'
match = re.search(pattern, html, re.DOTALL)
if not match:
    print("ERROR: FALLBACK_JOBS not found in HTML")
    exit(1)

# Get existing fallback jobs content (to append after new jobs)
existing_fb_content = match.group(2).strip()

# Build new jobs lines
new_lines = []
for j in new_jobs:
    line = json.dumps(j, ensure_ascii=False, separators=(',', ':'))
    new_lines.append('  ' + line)

new_fb_prefix = '\n' + ',\n'.join(new_lines) + ','

new_section = match.group(1) + new_fb_prefix + '\n  ' + existing_fb_content + '\n' + match.group(3)
new_html = html[:match.start()] + new_section + html[match.end():]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"HTML updated: prepended {len(new_jobs)} new jobs to FALLBACK_JOBS")
