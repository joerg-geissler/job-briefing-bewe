"""
fetch_emails.py — Holt Job-Alert-E-Mails via Microsoft Graph API (App-only / client credentials).
Liest senders.json, fragt pro Absender die letzten DAYS_BACK Tage ab,
speichert alle E-Mails als fetched_emails.json.

Benoetigte Umgebungsvariablen:
  AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, OUTLOOK_USER
"""
import os, json, sys
from datetime import datetime, timedelta, timezone

import msal
import requests

TENANT_ID     = os.environ["AZURE_TENANT_ID"]
CLIENT_ID     = os.environ["AZURE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
OUTLOOK_USER  = os.environ["OUTLOOK_USER"]
SENDERS_PATH  = os.environ.get("SENDERS_PATH", "senders.json")
OUTPUT_PATH   = "fetched_emails.json"
DAYS_BACK     = int(os.environ.get("DAYS_BACK", "2"))


def get_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise RuntimeError(f"Auth fehlgeschlagen: {result.get('error_description', result)}")
    return result["access_token"]


def fetch_for_sender(token, sender_email, source_label):
    since = (datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"https://graph.microsoft.com/v1.0/users/{OUTLOOK_USER}/messages"
    params = {
        "$filter":  f"from/emailAddress/address eq '{sender_email}' and receivedDateTime ge {since}",
        "$select":  "subject,bodyPreview,receivedDateTime,from",
        "$top":     25,
        "$orderby": "receivedDateTime desc",
    }
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
    r.raise_for_status()
    msgs = r.json().get("value", [])
    return [
        {
            "subject":          m.get("subject", ""),
            "bodyPreview":      m.get("bodyPreview", ""),
            "receivedDateTime": m.get("receivedDateTime", ""),
            "source":           source_label,
        }
        for m in msgs
    ]


def main():
    with open(SENDERS_PATH, encoding="utf-8") as f:
        senders = json.load(f)

    print(f"Authentifiziere mit Azure (Tenant: {TENANT_ID[:8]}...)")
    token = get_token()
    print("  Token OK")

    all_emails = []
    for s in senders:
        try:
            emails = fetch_for_sender(token, s["sender"], s["source"])
            print(f"  {s['source']}: {len(emails)} E-Mail(s)")
            all_emails.extend(emails)
        except Exception as e:
            print(f"  FEHLER {s['source']}: {e}", file=sys.stderr)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_emails, f, ensure_ascii=False, indent=2)

    print(f"FETCH_DONE: {len(all_emails)} E-Mails von {len(senders)} Absendern -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
