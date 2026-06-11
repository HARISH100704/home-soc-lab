"""response/notify.py — Send alerts to Telegram."""
import os
import requests
import logging

log = logging.getLogger("notify")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")


def send_telegram_alert(message: str) -> bool:
    if not BOT_TOKEN or not CHAT_ID:
        log.warning("Telegram not configured — skipping notification")
        return False
    try:
        url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id":    CHAT_ID,
            "text":       f"🛡️ *SOC ALERT*\n\n{message}",
            "parse_mode": "Markdown"
        }, timeout=10)
        resp.raise_for_status()
        log.info("Telegram alert sent")
        return True
    except Exception as e:
        log.error(f"Telegram error: {e}")
        return False
