import json

path = r'C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\index.html'
with open(path, encoding='utf-8') as f:
    content = f.read()

new_jobs_str = (
    '{"title": "Content Creator / Quereinsteiger (m/w/d) Marketing Manager (online)", "company": "Talentspring Marketing Academy", "location": "M\\u00fcnchen", "url": "", "salary_text": "", "salary_val": 0, "source": "Indeed Alert", "date_added": "2026-06-15", "pub_date": "", "mail_date": "2026-06-14", "score": 75},\n'
    '{"title": "Fotograf / Quereinsteiger (m/w/d) Marketing Manager (online)", "company": "Talentspring Marketing Academy", "location": "M\\u00fcnchen", "url": "", "salary_text": "", "salary_val": 0, "source": "Indeed Alert", "date_added": "2026-06-15", "pub_date": "", "mail_date": "2026-06-14", "score": 75},\n'
    '{"title": "SEA Job", "company": "Deep Media Technologies GmbH", "location": "M\\u00fcnchen", "url": "", "salary_text": "", "salary_val": 0, "source": "Indeed Alert", "date_added": "2026-06-15", "pub_date": "", "mail_date": "2026-06-14", "score": 75},\n'
    '{"title": "Senior Cloud Engineer Google", "company": "SWR S\\u00fcdwestrundfunk Anstalt des \\u00f6ffentlichen Rechts", "location": "Baden-Baden, Deutschland", "url": "", "salary_text": "", "salary_val": 0, "source": "#GOOGLE", "date_added": "2026-06-15", "pub_date": "2026-06-13", "mail_date": "2026-06-14", "score": 53},\n'
    '{"title": "Werkstudent (m/w/d) Generative AI - Google Cloud", "company": "Reply Group", "location": "D\\u00fcsseldorf, Deutschland", "url": "", "salary_text": "", "salary_val": 0, "source": "#GOOGLE", "date_added": "2026-06-15", "pub_date": "2026-06-12", "mail_date": "2026-06-13", "score": 53},\n'
)

old_anchor = 'const ALL_JOBS = [\n'
new_anchor = 'const ALL_JOBS = [\n' + new_jobs_str
content = content.replace(old_anchor, new_anchor, 1)

content = content.replace('Stand 2026-06-09 &middot; 236 Stellen', 'Stand 2026-06-15 &middot; 261 Stellen')
content = content.replace("const TODAY = '2026-06-12';", "const TODAY = '2026-06-15';")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('OK: index.html updated')
