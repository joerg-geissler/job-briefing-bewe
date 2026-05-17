"""
Telegram-Benachrichtigung fuer Job-Briefing BEWE.
Liest Konfiguration aus telegram.json, Nachricht aus telegram_msg.txt.
Kein Chrome benötigt – direkter HTTPS-Aufruf via Python urllib.
"""
import json, urllib.request, urllib.parse, sys, os

CONFIG_PATH = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Scheduled\job-briefing-bewe\telegram.json"
MSG_PATH    = r"C:\Users\joerg\job-briefing-public\telegram_msg.txt"

try:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
except FileNotFoundError:
    print("SKIP: telegram.json nicht gefunden")
    sys.exit(0)

if not cfg.get("enabled", False):
    print("SKIP: Telegram deaktiviert")
    sys.exit(0)

try:
    with open(MSG_PATH, encoding="utf-8") as f:
        text = f.read().strip()
except FileNotFoundError:
    print("FEHLER: telegram_msg.txt nicht gefunden")
    sys.exit(1)

if not text:
    print("SKIP: Leere Nachricht")
    sys.exit(0)

url  = f"https://api.telegram.org/bot{cfg['token']}/sendMessage"
data = urllib.parse.urlencode({"chat_id": cfg["chat_id"], "text": text}).encode("utf-8")

try:
    resp   = urllib.request.urlopen(url, data, timeout=15)
    result = json.loads(resp.read().decode("utf-8"))
    if result.get("ok"):
        print("OK: Telegram gesendet")
    else:
        print(f"FEHLER: {result}")
        sys.exit(1)
except Exception as e:
    print(f"FEHLER: {e}")
    sys.exit(1)
