import json, os

DB = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json"

new_jobs = [
 {"title":"Pursuit Lead, Google Cloud Consulting (English, German)","company":"Google","location":"Berlin, Deutschland","url":"","salary_text":"","salary_val":0,"source":"#GOOGLE","date_added":"2026-06-06","pub_date":"2026-06-05","mail_date":"2026-06-06","score":76},
 {"title":"Content & Communications Manager (m/w/d) Teilzeit (20-25h)","company":"Saleshead Recruiting","location":"München","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-06","score":75},
 {"title":"Appointment Setter (m/w/d) - remote","company":"BDE Sales Partners GmbH","location":"München","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-04","score":68},
 {"title":"Senior Marketplace Advertising Manager (m/w/d)","company":"VITAFY BRANDS","location":"München","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-06","score":60},
 {"title":"Product Owner / Product Manager (all genders)","company":"EnopAI GmbH & Co. KG","location":"München","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-06","score":60},
 {"title":"Senior E-Commerce Manager (m/w/d)","company":"Energiecheck24","location":"München","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-05","score":60},
 {"title":"Software Engineer III, AI/ML, Gemini Integration/Customisation","company":"Google","location":"München, Deutschland","url":"","salary_text":"","salary_val":0,"source":"#GOOGLE","date_added":"2026-06-06","pub_date":"2026-06-05","mail_date":"2026-06-06","score":60},
 {"title":"Mitarbeiter Interviewer (m/w/d)","company":"Forschungsgruppe Wahlen e.V.","location":"Mecklenburg-Vorpommern","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-06","pub_date":"","mail_date":"2026-06-05","score":50},
]

with open(DB, encoding="utf-8") as f:
    data = json.load(f)

def key(j):
    return (str(j.get("company",""))+"|"+str(j.get("title",""))+"|"+str(j.get("location",""))).lower()

existing = {key(j) for j in data}
add = [j for j in new_jobs if key(j) not in existing]

data = add + data

with open(DB, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("PREPEND: added=%d total=%d" % (len(add), len(data)))
for j in add:
    print(" +", j["score"], j["title"], "|", j["company"])
