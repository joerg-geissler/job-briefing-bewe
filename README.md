# job-briefing-bewe

Tägliches automatisches Job-Briefing für Joerg Geissler.  
Ein Claude-gesteuerter Workflow liest Job-Alert-Mails aus Outlook, bewertet und dedupliziert Stellenangebote, und veröffentlicht sie auf einem persönlichen Dashboard.

**Live-Dashboard:** https://joerg-geissler.github.io/job-briefing-bewe/

---

## Übersicht

```
Outlook-Mails (9 Absender)
        │
        ▼
Claude (Scheduled Task, täglich 07:06 Uhr)
        │
        ├─► Extraktion  (subject + bodyPreview only, kein Mail-Body)
        ├─► Scoring     (profile.json)
        ├─► Dedup       (company|title|location-Schlüssel)
        │
        ├─► jobs_dashboard.json  (JSON-Datenbank, Primärquelle)
        ├─► jobs.db              (SQLite, für generate.py)
        ├─► index.html           (Cowork-Dashboard)
        │
        └─► GitHub Pages (dieses Repo) + Telegram-Notification
```

---

## Dateien in diesem Repo

| Datei | Zweck |
|---|---|
| `SKILL.md` | **Task-Anweisung für Claude** — vollständige Schritt-für-Schritt-Logik |
| `senders.json` | Liste der Outlook-Absender mit source-Label |
| `profile.json` | Scoring-Gewichte (hard_exclude, tech_exclude, criteria) |
| `jobs_dashboard.json` | JSON-Datenbank aller gesammelten Stellen |
| `update_db.py` | Sync jobs_dashboard.json → jobs.db (SQLite) |
| `generate.py` | Erzeugt index.html aus jobs.db für GitHub Pages |
| `send_telegram.py` | Sendet Abschluss-Benachrichtigung via Telegram Bot |
| `index.html` | Das öffentliche Dashboard (GitHub Pages) |
| `.gitignore` | Schließt Secrets (telegram.json) und jobs.db aus |

### Nicht im Repo (lokal / OneDrive)
| Pfad | Inhalt |
|---|---|
| `...\Scheduled\job-briefing-bewe\telegram.json` | Bot-Token + Chat-ID (Secret!) |
| `...\Artifacts\job-briefing-bewe\jobs_dashboard.json` | Primäre JSON-DB (Canonical) |
| `...\Artifacts\job-briefing-bewe\index.html` | Cowork-Dashboard (lokale Kopie) |


---

## Ablauf (SKILL.md, Schritt A–J)

### A — Scoring-Profil laden
`profile.json` definiert alle Scoring-Regeln dynamisch. Kein hartkodiertes Scoring in der Task-Logik.

### B — Job-Datenbank laden
`jobs_dashboard.json` wird geladen. Daraus wird ein Set von Dedup-Schlüsseln erstellt:
```
(company + "|" + title + "|" + location).toLowerCase()
```

### C — Mails suchen (parallel)
Alle Einträge aus `senders.json` werden gleichzeitig via Outlook-MCP abgefragt:
```
outlook_email_search(sender, afterDateTime: heute-2Tage, limit: 25)
```
Nur `subject` + `bodyPreview` — kein Mail-Body (Token-Limit).

### D — Stellen extrahieren
Parsing nach source-Label:

| Source | Parsing-Regel |
|---|---|
| `#GOOGLE` | bodyPreview: `Titel\nFirma\nOrt\nüber Quelle` |
| `Indeed Alert/Archiv` | subject: Jobtitel-Liste, bodyPreview: erster Job |
| `Indeed Match` | subject: `Jobtitel bei Firma` |
| `Experteer` | subject: Jobtitel, bodyPreview: Firma/Ort |
| `Stepstone` | subject: `Deine Chancen stehen gut` → Titel; `X Firmen suchen` → skip |
| `Xing` | subject + bodyPreview generisch |
| `LinkedIn` (jobs-listings@) | subject: `You may be a fit for [Firma]'s [Titel] role`; pub_date aus `Posted on M/D/YYYY` |
| `LinkedIn` (jobalerts-noreply@) | `has been created` / `See your latest job matches` → überspringen |

pub_date-Extraktion:
- `#GOOGLE`: `"20. Mai"` → `"2026-05-20"` (deutsches Datumsformat)
- `LinkedIn (jobs-listings)`: `"Posted on 6/10/2026"` → `"2026-06-10"` (amerikanisches Format)

### E — Scoring
Reihenfolge: hard_exclude → tech_exclude → base + criteria-Summe

| Kategorie | Punkte | Beispiel-Begriffe |
|---|---|---|
| Basis | 50 | — |
| hard_exclude | = 5 | Junior, Trainee, Praktikum, Außendienst |
| tech_exclude | = 10 | C++, Golang, DevOps, SAP Basis |
| senior | +15 | Director, Head of, Lead, VP, Chief |
| marketing | +15 | Marketing, Digital, Growth, SEO, Performance |
| meaning | +20 | nachhaltig, NGO, sozial, Stiftung, Bildung |
| munich | +10 | München, Garching, Starnberg, … |
| remote | +8 | remote, homeoffice |
| consulting | +8 | Interim, Fractional, Advisor, Berater |
| deutschland | +3 | Deutschland |
| salary_bonus | +4 | Gehalt ≥ 75.000 € |

### F — Deduplizieren
Nur Stellen mit neuem `company|title|location`-Schlüssel werden aufgenommen.

### G — Datenbank aktualisieren
Neue Jobs (Score absteigend sortiert) werden an den Anfang von `jobs_dashboard.json` prepended.  
Anschließend: `update_db.py` → SQLite-Sync + daily_runs-Eintrag.

### H — Cowork-Dashboard aktualisieren
`index.html` (lokal) + Cowork-Artefakt `job-briefing-bewe` werden mit neuen Jobs aktualisiert.

### I — GitHub Pages aktualisieren
```bash
python generate.py
git add index.html && git commit -m auto-update & git push
```

### J — Telegram-Benachrichtigung
```
✅ Job-Briefing 2026-06-15 — 8 neue Stellen | Gesamt: 263 | Top: [Titel] (Score 90).
Dashboard: https://joerg-geissler.github.io/job-briefing-bewe/
```


---

## Konfiguration

### senders.json
```json
[
  { "sender": "donotreply@jobalert.indeed.com",  "source": "Indeed Alert" },
  { "sender": "donotreply@match.indeed.com",     "source": "Indeed Match" },
  { "sender": "alert@indeed.com",                "source": "Indeed Archiv" },
  { "sender": "jobs@mail.xing.com",              "source": "Xing" },
  { "sender": "notify-noreply@google.com",       "source": "#GOOGLE" },
  { "sender": "info@jobagent.stepstone.de",      "source": "Stepstone" },
  { "sender": "jobs@experteer.com",              "source": "Experteer" },
  { "sender": "jobalerts-noreply@linkedin.com",  "source": "LinkedIn" },
  { "sender": "jobs-listings@linkedin.com",      "source": "LinkedIn" }
]
```

### profile.json (Auszug)
```json
{
  "base": 50,
  "hard_exclude": { "score": 5, "terms": ["Junior", "Trainee", "Praktikum", ...] },
  "tech_exclude":  { "score": 10, "terms": ["C++", "Golang", "DevOps", ...] },
  "criteria": [ ... ]
}
```
→ Vollständige Datei: [profile.json](./profile.json)

---

## Lokale Dateipfade (Windows)

```
C:\Users\joerg\
├── job-briefing-public\               ← dieses Repo
│   ├── SKILL.md
│   ├── senders.json
│   ├── profile.json
│   ├── jobs_dashboard.json
│   ├── update_db.py
│   ├── generate.py
│   ├── send_telegram.py
│   └── index.html
│
└── OneDrive - die-weboptimierer\Dokumente\Claude\
    ├── Scheduled\job-briefing-bewe\
    │   ├── SKILL.md          ← Canonical (vom Scheduler gelesen)
    │   ├── senders.json      ← Canonical
    │   ├── profile.json      ← Canonical
    │   └── telegram.json     ← SECRET (nicht im Repo!)
    │
    └── Artifacts\job-briefing-bewe\
        ├── jobs_dashboard.json   ← Canonical JSON-DB
        └── index.html            ← Cowork-Dashboard
```

**Hinweis:** Die kanonischen Dateien liegen auf OneDrive (Scheduled-Ordner).  
Das GitHub-Repo enthält Kopien für Versionskontrolle und Dokumentation.  
Bei Konfigurationsänderungen: erst OneDrive-Datei anpassen, dann Repo-Kopie synchronisieren.

---

## Secrets einrichten

`telegram.json` muss lokal vorhanden sein (wird nicht committet):
```json
{
  "bot_token": "DEIN_BOT_TOKEN",
  "chat_id": "DEINE_CHAT_ID"
}
```
Pfad: `C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Scheduled\job-briefing-bewe\telegram.json`

---

## Scheduled Task

- **Task-ID:** `job-briefing-bewe`
- **Schedule:** täglich 07:06 Uhr (lokale Zeit)
- **Plattform:** Claude Cowork (Scheduled Tasks)
- **Anweisung:** `SKILL.md` (in diesem Repo und auf OneDrive)

---

## Weiterentwicklung

Typische Erweiterungen:
- **Neuen Absender hinzufügen:** Eintrag in `senders.json` + Parsing-Regel in `SKILL.md` Step D
- **Scoring anpassen:** `profile.json` → criteria-Array bearbeiten
- **Neues Dashboard-Feature:** `generate.py` und/oder `index.html` anpassen
- **Zweiten Telegram-Empfänger:** `send_telegram.py` erweitern

Nach jeder Änderung:
```bash
git add -A && git commit -m "beschreibung" && git push
```
Und OneDrive-Dateien manuell synchronisieren (SKILL.md, senders.json, profile.json).
