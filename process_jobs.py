#!/usr/bin/env python3
import json, re, sys

# Load existing DB
db_path = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json"
try:
    with open(db_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)
except:
    existing = []

dedup_set = set()
for j in existing:
    key = (j.get('company','') + '|' + j.get('title','') + '|' + j.get('location','')).lower()
    dedup_set.add(key)

print(f"Existing jobs: {len(existing)}, dedup keys: {len(dedup_set)}")

# Profile
profile = {
    "base": 50,
    "hard_exclude": {"score": 5, "terms": ["Junior", "Trainee", "Praktikum", "Außendienst", "Reinigung", "Lager", "Gasoline"]},
    "tech_exclude": {"score": 10, "terms": ["C++", "Java backend", "Golang", "DevOps", "SAP Basis", "ML Engineer"]},
    "criteria": [
        {"name": "senior", "points": 15, "terms": ["Director", "Head of", "Lead", "GF", "Interim", "Advisor", "Beirat", "Chief", "VP", "Abteilungsleitung"]},
        {"name": "marketing", "points": 15, "terms": ["Marketing", "Digital", "Growth", "Brand", "SEO", "SEA", "CRO", "UX", "Content", "Performance", "CRM", "Communications", "PR", "Werbung"]},
        {"name": "meaning", "points": 20, "terms": ["impact", "sinn", "nachhaltig", "sustain", "non-profit", "ngo", "sozial", "stiftung", "bildung", "pflege", "care", "klima", "charity", "gemeinnützig", "e.V."]},
        {"name": "munich", "points": 10, "terms": ["münchen", "munich", "garching", "oberhaching", "ismaning", "karlsfeld", "gräfelfing", "olching", "planegg", "starnberg", "otterfing"]},
        {"name": "remote", "points": 8, "terms": ["remote", "homeoffice", "home office"]},
        {"name": "consulting", "points": 8, "terms": ["consult", "strategy", "beratung", "interim", "fractional", "advisor", "berater"]},
        {"name": "deutschland", "points": 3, "terms": ["deutschland"]},
        {"name": "salary_bonus", "points": 4, "salary_threshold": 75000},
    ]
}

def score_job(title, location):
    text = (title + ' ' + location).lower()
    # hard exclude
    for t in profile['hard_exclude']['terms']:
        if t.lower() in text:
            return profile['hard_exclude']['score']
    # tech exclude
    for t in profile['tech_exclude']['terms']:
        if t.lower() in text:
            return profile['tech_exclude']['score']
    s = profile['base']
    for c in profile['criteria']:
        if 'salary_threshold' in c:
            continue
        for t in c['terms']:
            if t.lower() in text:
                s += c['points']
                break
    return s

# Raw jobs extracted from emails
raw_jobs = [
    # BEWE folder
    {"title": "Marketing-Manager (m/w/d) Recht / Steuern / Wirtschaft", "company": "Verlag C.H.Beck", "location": "München", "source": "# # # [BEWE]", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-03"},
    {"title": "UI/UX Designer / Quereinsteiger (m/w/d) Marketing Manager (online)", "company": "Talentspring Marketing Academy", "location": "München", "source": "# # # [BEWE]", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-03"},
    {"title": "Projekt Manager Marketing (m/w/d)", "company": "Saleshead Recruiting", "location": "München", "source": "# # # [BEWE]", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-02"},
    {"title": "Senior Content Manager SEO/AEO (m/w/d) befristet auf 1 Jahr", "company": "AutoScout24", "location": "München", "source": "# # # [BEWE]", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-02"},
    {"title": "Teamlead Digital Marketing (m/f/d)", "company": "Onepage GmbH", "location": "Deutschland", "source": "# # # [BEWE]", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-02"},
    {"title": "Senior SEA Manager", "company": "Stadtbranchenbuch München Vertriebs GmbH", "location": "Gräfelfing", "source": "# # # [BEWE]", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-02"},
    {"title": "Junior Brand Manager (m/w/d)", "company": "HERMES ARZNEIMITTEL GmbH", "location": "München", "source": "# # # [BEWE]", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-02"},
    {"title": "Projektmanager Cover/Grafik (m/w/d) dtv", "company": "Landesverband Nord e. V.", "location": "München", "source": "# # # [BEWE]", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-02"},
    {"title": "Social Media Manager (m/w/d)", "company": "gestalTeam", "location": "Deutschland", "source": "# # # [BEWE]", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-01"},
    {"title": "Leiter eCommerce", "company": "Büroservice - Organisation - Beratung", "location": "München", "source": "# # # [BEWE]", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-01"},
    # GOOGLE folder
    {"title": "Google Alliance Analyst (w/m/d)", "company": "PwC Germany", "location": "München", "source": "#GOOGLE", "date_added": "2026-06-03", "pub_date": "2026-05-31", "mail_date": "2026-06-03"},
    {"title": "SEA Team Lead - Google / Bing / SEMrush (m/f/d)", "company": "We Love X GmbH", "location": "Berlin", "source": "#GOOGLE", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-03"},
    {"title": "Forward Deployed Engineer, Applied AI, Google Cloud", "company": "Google", "location": "Berlin", "source": "#GOOGLE", "date_added": "2026-06-03", "pub_date": "2026-06-01", "mail_date": "2026-06-02"},
    {"title": "Senior Consultant (m/w/d) Google Cloud Platform & Google Looker", "company": "INFOMOTION GmbH", "location": "Straßlach-Dingharting", "source": "#GOOGLE", "date_added": "2026-06-03", "pub_date": "2026-06-01", "mail_date": "2026-06-01"},
    # Stepstone
    {"title": "Performance Marketing Manager (m/w/d)", "company": "", "location": "5752", "source": "Stepstone", "date_added": "2026-06-03", "pub_date": "", "mail_date": "2026-06-02"},
]

new_jobs = []
seen_keys = set()  # dedup within batch

for j in raw_jobs:
    key = (j['company'] + '|' + j['title'] + '|' + j['location']).lower()
    if key in dedup_set or key in seen_keys:
        print(f"SKIP (dup): {j['title']} @ {j['company']}")
        continue
    seen_keys.add(key)
    j['url'] = ''
    j['salary_text'] = ''
    j['salary_val'] = 0
    j['score'] = score_job(j['title'], j['location'])
    new_jobs.append(j)
    print(f"NEW (score={j['score']}): {j['title']} @ {j['company']} | {j['location']}")

new_jobs.sort(key=lambda x: x['score'], reverse=True)
print(f"\n=== {len(new_jobs)} neue Jobs ===")
for j in new_jobs[:5]:
    print(f"  {j['score']}: {j['title']} @ {j['company']}")

# Write new jobs list for import
with open(r'C:\Users\joerg\job-briefing-public\new_jobs.json', 'w', encoding='utf-8') as f:
    json.dump(new_jobs, f, ensure_ascii=False, indent=2)

print(f"DONE: {len(new_jobs)} new jobs written to new_jobs.json")
