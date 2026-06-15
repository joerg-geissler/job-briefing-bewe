# -*- coding: utf-8 -*-
import json
P = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json"
cands = [
{"title":"Head of Growth Marketing (m/w/d) bei FEIYR","company":"DANCE ALL DAY Musicvertriebs GmbH","location":"München","url":"","salary_text":"68.000 € - 91.000 €","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-12","pub_date":"","mail_date":"2026-06-10","score":94},
{"title":"(Senior) Kundenberater Digitales Marketing (all genders)","company":"Deep Media Technologies GmbH","location":"München","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-12","pub_date":"","mail_date":"2026-06-11","score":83},
{"title":"Manager Leadgenerierung & Immobilienmarketing (m/w/d)","company":"Bunz & Co Immobilien GmbH","location":"Deutschland","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-12","pub_date":"","mail_date":"2026-06-11","score":83},
{"title":"Initiativbewerbung - Google Ads Agentur (m/w/d) - 100% Remote - Werde Teil unserer Growth Story!","company":"Beilmann Marketing GmbH","location":"Deutschland","url":"","salary_text":"","salary_val":0,"source":"#GOOGLE","date_added":"2026-06-12","pub_date":"2026-06-10","mail_date":"2026-06-11","score":76},
{"title":"Influencer Marketing Manager (m/w/d)","company":"M. Asam GmbH","location":"München","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-12","pub_date":"","mail_date":"2026-06-11","score":75},
{"title":"Manager Brand Management (m/w/d)","company":"M. Asam GmbH","location":"München","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-12","pub_date":"","mail_date":"2026-06-10","score":75},
{"title":"Marketing Koordinator*","company":"F.S. KUSTERMANN GMBH","location":"Deutschland","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-12","pub_date":"","mail_date":"2026-06-10","score":68},
{"title":"Senior Marketing, Communications and Brand Manager (m/f/d)","company":"Integrity Next GmbH","location":"","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-12","pub_date":"","mail_date":"2026-06-11","score":65},
{"title":"Lead, Energy Strategic Negotiator (Finnish, English)","company":"Google","location":"Multiple Sites","url":"","salary_text":"","salary_val":0,"source":"#GOOGLE","date_added":"2026-06-12","pub_date":"2026-06-11","mail_date":"2026-06-11","score":65},
{"title":"Einführungsprojekt Google Cloud (m/w/d)","company":"freelance.de","location":"München, Deutschland","url":"","salary_text":"","salary_val":0,"source":"#GOOGLE","date_added":"2026-06-12","pub_date":"2026-06-11","mail_date":"2026-06-12","score":63},
{"title":"(Senior) AI Customer Experience Manager (w/m/d)","company":"1&1 Telecommunication SE","location":"München","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-12","pub_date":"","mail_date":"2026-06-11","score":60},
{"title":"Technical Operations Manager, Third Party Data Center Facilities","company":"Google","location":"Hanau, Deutschland","url":"","salary_text":"","salary_val":0,"source":"#GOOGLE","date_added":"2026-06-12","pub_date":"2026-06-11","mail_date":"2026-06-12","score":53},
{"title":"(Junior) Customer Success Manager Marketing (all genders)","company":"Deep Media Technologies GmbH","location":"München","url":"","salary_text":"","salary_val":0,"source":"# # # [BEWE]","date_added":"2026-06-12","pub_date":"","mail_date":"2026-06-11","score":5},
{"title":"Junior Account Manager – Google Ads","company":"Cross Border Talents","location":"Nürnberg, Deutschland","url":"","salary_text":"","salary_val":0,"source":"#GOOGLE","date_added":"2026-06-12","pub_date":"","mail_date":"2026-06-12","score":5},
]

with open(P, encoding="utf-8") as f:
    db = json.load(f)
keys = {(j.get("company","")+"|"+j.get("title","")+"|"+j.get("location","")).lower() for j in db}
new = []
for c in cands:
    k = (c["company"]+"|"+c["title"]+"|"+c["location"]).lower()
    if k not in keys:
        keys.add(k)
        new.append(c)
new.sort(key=lambda x: -x["score"])
db = new + db
with open(P, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=4)
print("MERGE_NEW=%d TOTAL=%d" % (len(new), len(db)))
for c in new:
    print("JS:" + json.dumps(c, ensure_ascii=False))
