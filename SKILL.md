---
name: job-briefing-bewe
description: Tägliche Job-Auswertung: subject+bodyPreview only, Absender-Liste (senders.json), DB + Cowork-Artefakt + GitHub Pages (joerg-geissler.github.io/job-briefing-bewe)
---

Du führst die tägliche Auswertung der Job-Alert-Mails für Joerg Geissler durch.
Der Nutzer ist NICHT anwesend. Arbeite vollständig autonom – stelle KEINE Rückfragen,
öffne keine Dialoge, warte auf keine Benutzereingaben. Bei jedem Fehler: kurz melden, weitermachen.

FESTE DATEIPFADE – immer via mcp__Desktop_Commander__read_file / write_file:
- Scoring-Profil:  C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Scheduled\job-briefing-bewe\profile.json
- Absender-Liste:  C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Scheduled\job-briefing-bewe\senders.json
- Telegram-Config: C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Scheduled\job-briefing-bewe\telegram.json
- Job-Datenbank:   C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json
- Dashboard-HTML:  C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\index.html
- GitHub-Repo:     C:\Users\joerg\job-briefing-public\

WICHTIG: KEIN read_resource für E-Mail-Bodies — Token-Limit. Ausschließlich subject + bodyPreview verwenden.

═══ SCHRITT A: SCORING-GEWICHTE LADEN ═══
Lies profile.json via mcp__Desktop_Commander__read_file.
Falls nicht vorhanden → Standardgewichte:
{ base:50, senior:15, marketing:15, meaning:20, munich:10, remote:8, consulting:8, deutschland:3, salary_bonus:4 }

═══ SCHRITT B: JOB-DATENBANK LADEN ═══
Lies jobs_dashboard.json via mcp__Desktop_Commander__read_file.
Erstelle ein Set bestehender Dedup-Schlüssel: (company + "|" + title + "|" + location).toLowerCase()
Falls Datei fehlt → leeres Array + leeres Set.

═══ SCHRITT C: MAILS SUCHEN (Absender-Liste) ═══

1. Lies senders.json via mcp__Desktop_Commander__read_file.
   Falls Datei fehlt → Fallback-Liste verwenden:
   [
     {"sender": "donotreply@jobalert.indeed.com", "source": "Indeed Alert"},
     {"sender": "donotreply@match.indeed.com",    "source": "Indeed Match"},
     {"sender": "alert@indeed.com",               "source": "Indeed Archiv"},
     {"sender": "jobs@mail.xing.com",             "source": "Xing"},
     {"sender": "notify-noreply@google.com",      "source": "#GOOGLE"},
     {"sender": "info@jobagent.stepstone.de",     "source": "Stepstone"},
     {"sender": "jobs@experteer.com",             "source": "Experteer"}
   ]

2. Alle Absender GLEICHZEITIG in einem Schritt aufrufen (parallele Tool-Calls):
   Pro Eintrag in der Liste:
   mcp__ba9f12b3-d081-4e1e-8e5d-8aff31df6b9f__outlook_email_search
   { sender: "<sender>", afterDateTime: "<heute minus 2 Tage YYYY-MM-DD>", limit: 25 }

   Nur subject + bodyPreview auswerten. KEIN read_resource aufrufen.
   Den "source"-Wert aus der Liste als Quell-Label für Schritt D verwenden.

═══ SCHRITT D: STELLEN EXTRAHIEREN aus subject + bodyPreview ═══

Parsing nach source-Label:

source "#GOOGLE": bodyPreview enthält "Titel\nFirma\nOrt\nüber Quelle" – alle Blöcke extrahieren.
source "Indeed Alert" / "Indeed Archiv": subject zeigt Jobtitel-Liste, bodyPreview zeigt ersten Job mit Firma/Ort.
source "Indeed Match": subject = "Jobtitel bei Firma" → Titel + Firma direkt extrahieren.
source "Experteer": subject = Jobtitel, bodyPreview mit Firma/Ort – HOCHRELEVANT.
source "Stepstone":
  - "Deine Chancen stehen gut" im subject → Jobtitel extrahieren.
  - "X Firmen suchen..." → überspringen (keine verwertbaren Jobtitel).
source "Xing": subject + bodyPreview auswerten (enthält oft Titel, Firma, Ort, Gehalt).
source "LinkedIn" (Absender jobs-listings@linkedin.com):
  - subject-Muster: "You may be a fit for [Firma]'s [Titel] role"
    → Firma: Text zwischen "for " und "'s " | Titel: Text zwischen "'s " und " role"
  - pub_date aus bodyPreview: "Posted on M/D/YYYY" → umrechnen in YYYY-MM-DD (z. B. "6/10/2026" → "2026-06-10")
  - Falls kein "Posted on" im bodyPreview → pub_date: ""
source "LinkedIn" (Absender jobalerts-noreply@linkedin.com):
  - subject oder bodyPreview enthält "has been created" oder "See your latest job matches" ohne Jobtitel → Mail komplett überspringen.
  - Falls echte Jobtitel enthalten → generisch extrahieren.
Alle anderen sources: subject + bodyPreview generisch auswerten.

Pro extrahierter Stelle:
{
  "title": "<Titel>", "company": "<Firma oder leer>", "location": "<Ort oder leer>",
  "url": "", "salary_text": "<Gehalt aus bodyPreview oder leer>", "salary_val": 0,
  "source": "<source-Label>", "date_added": "<heute YYYY-MM-DD>",
  "pub_date": "<Veröffentlichungsdatum YYYY-MM-DD oder leer>",
  "mail_date": "<receivedDateTime des E-Mails als YYYY-MM-DD>",
  "score": 0
}

pub_date-Extraktion (nur aus subject + bodyPreview, kein read_resource):
- source "#GOOGLE": bodyPreview enthält Datumsangaben direkt nach der Quellenzeile,
  z.B. "über LinkedIn\n20. MaiVollzeit" oder "über Indeed\n19. Mai" → "20. Mai" → YYYY-MM-DD
  (Monatsnamen: Jan=01, Feb=02, Mär=03, Apr=04, Mai=05, Jun=06, Jul=07, Aug=08, Sep=09, Okt=10, Nov=11, Dez=12)
  Aktuelles Jahr verwenden. Beispiel: "20. Mai" bei Lauf 2026-05-21 → "2026-05-20"
- source "LinkedIn" (jobs-listings@linkedin.com): bodyPreview enthält "Posted on M/D/YYYY" → in YYYY-MM-DD umrechnen (amerikanisches Format). Beispiel: "Posted on 6/10/2026" → "2026-06-10". Falls nicht vorhanden → pub_date: ""
- Alle anderen sources: kein Datum im subject+bodyPreview sichtbar → pub_date: ""

mail_date: immer = receivedDateTime des jeweiligen E-Mails, gekürzt auf YYYY-MM-DD.
Beispiel: receivedDateTime "2026-05-20T14:37:06.000Z" → mail_date: "2026-05-20"

═══ SCHRITT E: SCORING ═══
Alle Scoring-Regeln kommen aus profile.json (dynamisch – keine hartkodierte Liste mehr hier).

Ablauf:
1. Prüfe hard_exclude.terms (case-insensitiv) gegen title+location → wenn Treffer: Score = hard_exclude.score, fertig.
2. Prüfe tech_exclude.terms (case-insensitiv) gegen title+location → wenn Treffer: Score = tech_exclude.score, fertig.
3. Startpunkt: base
4. Iteriere criteria-Array:
   - Falls Eintrag hat "salary_threshold": addiere points wenn salary_val ≥ salary_threshold ODER salary_text enthält erkennbaren Jahreswert ≥ threshold.
   - Sonst: prüfe terms (case-insensitiv) gegen title+location → wenn mind. 1 Treffer: addiere points.
5. Fertig → score speichern.

═══ SCHRITT F: DEDUPLIZIEREN ═══
Dedup-Schlüssel: (company + "|" + title + "|" + location).toLowerCase()
Nur Jobs mit Schlüssel, der NICHT im bestehenden Set ist → neue Jobs.

═══ SCHRITT G: DATENBANK AKTUALISIEREN ═══
Neue Jobs (sortiert nach Score absteigend) am Anfang von jobs_dashboard.json einfügen.
Methode: mcp__Desktop_Commander__edit_block – old_string: die ersten 2-3 Zeilen des ersten bestehenden Jobs.

═══ SCHRITT G2: SQLITE-DATENBANK AKTUALISIEREN ═══
Python-Script aufrufen (neue Jobs + Status-Sync + daily_runs-Eintrag):

mcp__Desktop_Commander__start_process:
  shell: cmd
  timeout_ms: 20000
  command: python C:\Users\joerg\job-briefing-public\update_db.py

Erwartete Ausgabe: "DB_UPDATE: new=<N> total=<T> top_score=<S> status_synced=<X>"
Den Wert "new=<N>" merken fuer den Abschlussbericht.
Bei Fehler: kurz melden, weitermachen.

═══ SCHRITT H: COWORK-DASHBOARD AKTUALISIEREN ═══
1. mcp__Desktop_Commander__edit_block auf index.html:
   - old_string: `JOBS = [` + erste Zeile des ersten bestehenden Jobs (als Anker)
   - new_string: `JOBS = [` + neue Jobs als kompakte Einzeiler + gleicher Anker

2. Datei in Outputs-Verzeichnis kopieren (Pfad steht im Systemkontext unter "Working directory"):
   mcp__Desktop_Commander__start_process:
   shell: powershell.exe
   timeout_ms: 15000
   command: Copy-Item -Path "C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\index.html" -Destination "<OUTPUTS-PFAD>\index.html" -Force; Write-Output "OK"
   → <OUTPUTS-PFAD> aus dem Systemkontext ermitteln (Working directory des aktuellen Sessions)

3. mcp__cowork__update_artifact: id="job-briefing-bewe", html_path=<outputs-pfad>/index.html

═══ SCHRITT I: GITHUB PAGES AKTUALISIEREN ═══

1. Python-Script ausführen:
   mcp__Desktop_Commander__start_process:
   shell: cmd
   timeout_ms: 25000
   command: python C:\Users\joerg\job-briefing-public\generate.py
   → Prüfe Output auf "OK:" — bei Fehler kurz melden und weitermachen.

2. Git commit & push — WICHTIG: Kein Leerzeichen in der Commit-Message, keine Anführungszeichen:
   mcp__Desktop_Commander__start_process:
   shell: cmd
   timeout_ms: 35000
   command: cd /d C:\Users\joerg\job-briefing-public && git add index.html && git -c core.editor=true commit -m auto-update & git push
   HINWEIS: Einzelnes & vor git push (nicht &&) → push läuft auch wenn "nothing to commit"
   HINWEIS: git -c core.editor=true verhindert, dass ein Texteditor geöffnet wird

═══ SCHRITT J: ABSCHLUSSBERICHT + TELEGRAM ═══

Abschlussbericht erstellen:
- Anzahl neue Stellen pro Absender/source
- Top 3 neue Stellen mit Score ≥80: Titel + Firma + Score + 1-Satz Begründung
- Öffentliche URL: https://joerg-geissler.github.io/job-briefing-bewe/
- Hinweis: Da nur subject+bodyPreview, können Firma/Ort teilweise leer sein

Telegram-Benachrichtigung — KEIN Chrome, KEIN Skill — direkt via Python:

1. Schreibe eine kurze Zusammenfassung (max. 300 Zeichen) nach:
   C:\Users\joerg\job-briefing-public\telegram_msg.txt
   via mcp__Desktop_Commander__write_file
   Inhalt z.B.: "✅ Job-Briefing <DATUM> — <N> neue Stellen | Gesamt: <T> | Top: <Top1-Titel> (Score <X>). Dashboard: https://joerg-geissler.github.io/job-briefing-bewe/"
   Werte <N> und <T> aus der DB_UPDATE-Ausgabe (Schritt G2) verwenden.

2. Python-Script ausführen:
   mcp__Desktop_Commander__start_process:
   shell: cmd
   timeout_ms: 20000
   command: python C:\Users\joerg\job-briefing-public\send_telegram.py
   → "OK: Telegram gesendet" → Ausgabe: "📱 Telegram-Benachrichtigung gesendet."
   → Fehler → kurz melden, Aufgabe trotzdem als abgeschlossen betrachten

Bei Fehlern in einzelnen Schritten: kurz berichten und mit nächstem Schritt weitermachen.