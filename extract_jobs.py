"""
extract_jobs.py — Extrahiert Stellenangebote aus fetched_emails.json via Claude API (Haiku),
wendet Scoring aus profile.json an, dedupliziert gegen jobs_dashboard.json
und schreibt neue Eintraege ans Ende / vor die bestehenden.

Benoetigte Umgebungsvariablen:
  ANTHROPIC_API_KEY
"""
import os, json, sys
from datetime import date

import anthropic

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
EMAILS_PATH  = os.environ.get("EMAILS_PATH",  "fetched_emails.json")
DB_PATH      = os.environ.get("DB_PATH",      "jobs_dashboard.json")
PROFILE_PATH = os.environ.get("PROFILE_PATH", "profile.json")
TODAY        = date.today().isoformat()

SYSTEM_PROMPT = """Du bist ein Job-Extraktions-Assistent. Du bekommst E-Mail-Daten (subject + bodyPreview) von Job-Alert-Diensten und extrahierst daraus Stellenangebote.

PARSING-REGELN nach source-Label:
- "#GOOGLE": bodyPreview enthaelt "Titel\nFirma\nOrt\nueber Quelle\nDatum" - alle Bloecke extrahieren. pub_date: Datum nach der Quellenzeile (z.B. "20. Mai" -> aktuelles Jahr + MM-DD, Monatsnamen: Jan=01, Feb=02, Maer=03, Apr=04, Mai=05, Jun=06, Jul=07, Aug=08, Sep=09, Okt=10, Nov=11, Dez=12).
- "Indeed Alert" / "Indeed Archiv": subject zeigt Jobtitel-Liste, bodyPreview zeigt ersten Job mit Firma/Ort.
- "Indeed Match": subject = "Jobtitel bei Firma" -> Titel + Firma direkt extrahieren.
- "Experteer": subject = Jobtitel, bodyPreview mit Firma/Ort.
- "Stepstone": "Deine Chancen stehen gut" im subject -> extrahieren; "X Firmen suchen..." -> ueberspringen.
- "Xing": subject + bodyPreview, oft mit Gehalt.
- "LinkedIn" (source enthaelt "LinkedIn", Absender jobs-listings@linkedin.com): subject-Muster "You may be a fit for [Firma]'s [Titel] role" -> Firma: Text zwischen "for " und "'s " | Titel: Text zwischen "'s " und " role". pub_date: "Posted on M/D/YYYY" aus bodyPreview -> YYYY-MM-DD umrechnen (z.B. "6/10/2026" -> "2026-06-10"). Falls kein "Posted on" -> pub_date: "".
- "LinkedIn" (Absender jobalerts-noreply@linkedin.com): subject/bodyPreview enthaelt "has been created" oder "See your latest job matches" ohne echten Jobtitel -> Mail komplett ueberspringen. Sonst echte Jobtitel extrahieren.
- Alle anderen: subject + bodyPreview generisch auswerten.

Fuer jede extrahierte Stelle ein Objekt:
{
  "title": "Jobtitel",
  "company": "Firmenname oder leer",
  "location": "Ort oder leer",
  "salary_text": "Gehaltsangabe oder leer",
  "source": "source-Label aus der E-Mail (z.B. 'LinkedIn', '#GOOGLE', 'Indeed Alert')",
  "pub_date": "YYYY-MM-DD oder leer",
  "mail_date": "YYYY-MM-DD (aus receivedDateTime)"
}

Gib NUR ein gueltiges JSON-Array zurueck, kein Markdown, keine Erklaerungen, keine Code-Blocks."""


def score_job(job, profile):
    text = f"{job.get('title','').lower()} {job.get('location','').lower()}"
    for t in profile["hard_exclude"]["terms"]:
        if t.lower() in text:
            return profile["hard_exclude"]["score"]
    for t in profile["tech_exclude"]["terms"]:
        if t.lower() in text:
            return profile["tech_exclude"]["score"]
    score = profile["base"]
    for crit in profile["criteria"]:
        if "salary_threshold" in crit:
            if job.get("salary_val", 0) >= crit["salary_threshold"]:
                score += crit["points"]
        else:
            if any(t.lower() in text for t in crit.get("terms", [])):
                score += crit["points"]
    return score


def extract_batch(client, emails_batch):
    """Sendet bis zu 10 E-Mails an Claude und gibt extrahierte Jobs zurueck."""
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Extrahiere alle Stellen. Heute: {TODAY}\n\n{json.dumps(emails_batch, ensure_ascii=False)}",
        }],
    )
    raw = resp.content[0].text.strip()
    # Robustheit: falls Markdown-Block
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def main():
    with open(EMAILS_PATH, encoding="utf-8") as f:
        emails = json.load(f)

    if not emails:
        print("Keine E-Mails zum Verarbeiten.")
        with open("telegram_msg.txt", "w", encoding="utf-8") as f:
            f.write(f"ℹ️ Job-Briefing {TODAY} — Keine neuen E-Mails.")
        return

    with open(DB_PATH, encoding="utf-8") as f:
        existing = json.load(f)

    with open(PROFILE_PATH, encoding="utf-8") as f:
        profile = json.load(f)

    # Dedup-Set aufbauen
    dedup = {
        f"{j.get('company','')}|{j.get('title','')}|{j.get('location','')}".lower()
        for j in existing
    }

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    new_jobs = []
    BATCH = 10

    for i in range(0, len(emails), BATCH):
        batch = emails[i : i + BATCH]
        print(f"  Batch {i//BATCH + 1}: {len(batch)} E-Mails...")
        try:
            jobs = extract_batch(client, batch)
        except Exception as e:
            print(f"  FEHLER Batch {i//BATCH + 1}: {e}", file=sys.stderr)
            continue

        for job in jobs:
            job.setdefault("url", "")
            job.setdefault("salary_val", 0)
            job.setdefault("source", "")
            job["date_added"] = TODAY
            job["score"] = score_job(job, profile)
            key = f"{job.get('company','')}|{job.get('title','')}|{job.get('location','')}".lower()
            if key not in dedup:
                dedup.add(key)
                new_jobs.append(job)

    new_jobs.sort(key=lambda x: x["score"], reverse=True)

    if new_jobs:
        updated = new_jobs + existing
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(updated, f, ensure_ascii=False, indent=4)
        print(f"  {len(new_jobs)} neue Jobs in {DB_PATH} geschrieben.")
    else:
        print("  Keine neuen Jobs (alles bereits in DB).")

    top = new_jobs[0] if new_jobs else None
    top_str = f"{top['title']} – {top.get('company','')} (Score {top['score']})" if top else "–"
    total = len(new_jobs) + len(existing)

    print(f"EXTRACT_DONE: new={len(new_jobs)} total={total} top={top_str}")

    # Telegram-Nachricht vorbereiten
    msg = (
        f"✅ Job-Briefing {TODAY} — {len(new_jobs)} neue Stellen | "
        f"Gesamt: {total} | Top: {top_str}. "
        f"Dashboard: https://joerg-geissler.github.io/job-briefing-bewe/"
    )
    with open("telegram_msg.txt", "w", encoding="utf-8") as f:
        f.write(msg[:300])


if __name__ == "__main__":
    main()
