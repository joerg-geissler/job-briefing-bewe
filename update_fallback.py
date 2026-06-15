import json

p = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\index.html"

new_jobs = [
 {"title":"Pursuit Lead, Google Cloud Consulting (English, German)","company":"Google","location":"Berlin, Deutschland","source":"#GOOGLE","date_added":"2026-06-06","pub_date":"2026-06-05","mail_date":"2026-06-06","url":"","salary_text":"","salary_val":0,"score":76},
 {"title":"Content & Communications Manager (m/w/d) Teilzeit (20-25h)","company":"Saleshead Recruiting","location":"München","source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-06","url":"","salary_text":"","salary_val":0,"score":75},
 {"title":"Appointment Setter (m/w/d) - remote","company":"BDE Sales Partners GmbH","location":"München","source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-04","url":"","salary_text":"","salary_val":0,"score":68},
 {"title":"Senior Marketplace Advertising Manager (m/w/d)","company":"VITAFY BRANDS","location":"München","source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-06","url":"","salary_text":"","salary_val":0,"score":60},
 {"title":"Product Owner / Product Manager (all genders)","company":"EnopAI GmbH & Co. KG","location":"München","source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-06","url":"","salary_text":"","salary_val":0,"score":60},
 {"title":"Senior E-Commerce Manager (m/w/d)","company":"Energiecheck24","location":"München","source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-05","url":"","salary_text":"","salary_val":0,"score":60},
 {"title":"Software Engineer III, AI/ML, Gemini Integration/Customisation","company":"Google","location":"München, Deutschland","source":"#GOOGLE","date_added":"2026-06-06","pub_date":"2026-06-05","mail_date":"2026-06-06","url":"","salary_text":"","salary_val":0,"score":60},
 {"title":"Mitarbeiter Interviewer (m/w/d)","company":"Forschungsgruppe Wahlen e.V.","location":"Mecklenburg-Vorpommern","source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-05","url":"","salary_text":"","salary_val":0,"score":50},
]

src = open(p, encoding="utf-8").read()
anchor = "const FALLBACK_JOBS = [\n"
idx = src.find(anchor)
if idx == -1:
    raise SystemExit("ANCHOR NOT FOUND")
ins = "".join("  " + json.dumps(j, ensure_ascii=False) + ",\n" for j in new_jobs)
out = src[:idx+len(anchor)] + ins + src[idx+len(anchor):]
open(p, "w", encoding="utf-8").write(out)
print("FALLBACK: inserted %d jobs" % len(new_jobs))
