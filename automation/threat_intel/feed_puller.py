"""
threat_intel/feed_puller.py
Pulls daily IOC feeds from OTX and saves to local blocklist.
Run this as a daily cron job:
  0 6 * * * python3 /path/to/feed_puller.py
"""

import os
import requests
import logging
from datetime import datetime, timedelta

log = logging.getLogger("feed_puller")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

OTX_KEY      = os.getenv("OTX_KEY", "")
OUTPUT_FILE  = os.path.join(os.path.dirname(__file__), "..", "data", "threat_feed_ips.txt")
BASE         = "https://otx.alienvault.com/api/v1"


def pull_otx_feed(days_back: int = 1) -> list[str]:
    """Pull malicious IPs from OTX pulses updated in the last N days."""
    if not OTX_KEY:
        log.error("OTX_KEY not set")
        return []

    since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%S")
    ips: list[str] = []
    page = 1

    while True:
        resp = requests.get(
            f"{BASE}/pulses/subscribed",
            headers={"X-OTX-API-KEY": OTX_KEY},
            params={"modified_since": since, "page": page, "limit": 50},
            timeout=15
        )
        if resp.status_code != 200:
            log.error(f"OTX error: {resp.status_code}")
            break

        data    = resp.json()
        pulses  = data.get("results", [])
        if not pulses:
            break

        for pulse in pulses:
            for indicator in pulse.get("indicators", []):
                if indicator.get("type") == "IPv4":
                    ips.append(indicator["indicator"])

        if not data.get("next"):
            break
        page += 1

    log.info(f"Pulled {len(ips)} IPs from OTX")
    return list(set(ips))


def save_feed(ips: list[str]):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"# OTX Threat Feed — updated {datetime.utcnow().isoformat()}\n")
        for ip in sorted(ips):
            f.write(f"{ip}\n")
    log.info(f"Saved {len(ips)} IPs to {OUTPUT_FILE}")


if __name__ == "__main__":
    ips = pull_otx_feed(days_back=1)
    save_feed(ips)
