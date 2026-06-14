"""
send_telegram_cloud.py — Sendet Telegram-Benachrichtigung via Bot API.
Liest Nachricht aus telegram_msg.txt, Token + Chat-ID aus Umgebungsvariablen.

Benoetigte Umgebungsvariablen:
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
"""
import os, sys
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")
MSG_PATH  = "telegram_msg.txt"

if not BOT_TOKEN or not CHAT_ID:
    print("TELEGRAM: keine Konfiguration, ueberspringe.")
    sys.exit(0)

try:
    with open(MSG_PATH, encoding="utf-8") as f:
        text = f.read().strip()
except FileNotFoundError:
    text = "✅ Job-Briefing abgeschlossen."

url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
resp = requests.post(url, json={"chat_id": CHAT_ID, "text": text})
data = resp.json()

if data.get("ok"):
    print("OK: Telegram gesendet")
else:
    print(f"FEHLER Telegram: {data}", file=sys.stderr)
    sys.exit(1)
