"""
soc_engine.py
Main automation loop — polls Wazuh, enriches alerts, triggers responses.
"""

import os
import time
import logging
from dotenv import load_dotenv
from enrichment.virustotal import check_ip_virustotal
from enrichment.abuseipdb  import check_abuseipdb
from enrichment.otx        import check_otx_ip
from enrichment.greynoise  import check_greynoise
from response.notify       import send_telegram_alert
from response.block_ip     import block_ip
from wazuh_client          import get_recent_alerts

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("data/soc_engine.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("soc_engine")

SCORE_NOTIFY = int(os.getenv("SCORE_NOTIFY", 50))
SCORE_BLOCK  = int(os.getenv("SCORE_BLOCK",  80))
POLL_SECS    = int(os.getenv("POLL_INTERVAL_SECONDS", 30))
MIN_LEVEL    = int(os.getenv("MIN_ALERT_LEVEL", 10))

processed: set = set()

PRIVATE_PREFIXES = ("10.", "192.168.", "172.16.", "172.17.",
                    "172.18.", "172.19.", "172.20.", "172.21.",
                    "172.22.", "172.23.", "172.24.", "172.25.",
                    "172.26.", "172.27.", "172.28.", "172.29.",
                    "172.30.", "172.31.", "127.", "0.")


def is_private(ip: str) -> bool:
    return any(ip.startswith(p) for p in PRIVATE_PREFIXES)


def score(vt: dict, abuse: dict, otx: dict, grey: dict) -> int:
    s = 0
    mal = vt.get("malicious", 0)
    s += 40 if mal >= 10 else 25 if mal >= 5 else 15 if mal >= 1 else 0

    ab = abuse.get("abuse_score", 0)
    s += 30 if ab >= 80 else 20 if ab >= 50 else 10 if ab >= 20 else 0

    pulses = otx.get("pulse_count", 0)
    s += 20 if pulses >= 5 else 12 if pulses >= 2 else 8 if pulses >= 1 else 0

    if grey.get("riot"):   s = max(0, s - 15)
    elif grey.get("noise"): s = max(0, s - 5)

    return min(s, 100)


def handle_alert(alert: dict):
    aid = alert.get("id", "")
    if aid in processed:
        return
    processed.add(aid)

    rule        = alert.get("rule", {})
    level       = rule.get("level", 0)
    description = rule.get("description", "Unknown")
    src_ip      = (alert.get("data", {}).get("srcip") or
                   alert.get("agent", {}).get("ip", ""))
    agent       = alert.get("agent", {}).get("name", "Unknown")
    timestamp   = alert.get("timestamp", "")

    log.info(f"[{aid}] L{level} | {description} | {src_ip} | {agent}")

    if not src_ip or is_private(src_ip):
        log.info(f"  Skipping private/missing IP: {src_ip}")
        return

    vt    = check_ip_virustotal(src_ip)
    abuse = check_abuseipdb(src_ip)
    otx   = check_otx_ip(src_ip)
    grey  = check_greynoise(src_ip)
    threat_score = score(vt, abuse, otx, grey)

    log.info(f"  Score: {threat_score}/100")

    msg = (
        f"*{description}*\n"
        f"Severity: Level {level}  |  Score: {threat_score}/100\n"
        f"IP: `{src_ip}` ({abuse.get('country','?')} — {abuse.get('isp','?')})\n"
        f"Host: {agent}  |  {timestamp}\n\n"
        f"VT malicious: {vt.get('malicious',0)} engines\n"
        f"AbuseIPDB: {abuse.get('abuse_score',0)}/100 "
        f"({abuse.get('total_reports',0)} reports)\n"
        f"OTX pulses: {otx.get('pulse_count',0)}\n"
        f"Greynoise: {'background noise' if grey.get('noise') else 'targeted'}"
    )

    if threat_score >= SCORE_BLOCK:
        log.warning(f"  → AUTO-BLOCKING {src_ip}")
        block_ip(src_ip)
        send_telegram_alert(f"🔴 AUTO-BLOCKED\n\n{msg}")
    elif threat_score >= SCORE_NOTIFY:
        log.warning(f"  → NOTIFY (high risk)")
        send_telegram_alert(f"🟠 HIGH RISK\n\n{msg}")
    else:
        log.info(f"  → Low risk, logged only")


def main():
    log.info("🛡️  SOC Engine started")
    while True:
        try:
            alerts = get_recent_alerts(limit=50, min_level=MIN_LEVEL)
            log.info(f"Fetched {len(alerts)} alerts (level ≥ {MIN_LEVEL})")
            for a in alerts:
                handle_alert(a)
        except Exception as e:
            log.error(f"Engine error: {e}", exc_info=True)
        time.sleep(POLL_SECS)


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    main()
