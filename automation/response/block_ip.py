"""
response/block_ip.py
Adds an IP to the local blocklist file.
On Linux you can also push this to iptables directly.
On pfSense, you'd call its API — see comments below.
"""
import os
import logging
import subprocess
from datetime import datetime

log = logging.getLogger("block_ip")

BLOCKLIST_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "blocked_ips.txt"
)

_blocked: set = set()


def block_ip(ip: str) -> bool:
    """Add IP to blocklist file + local iptables (if on Linux)."""
    os.makedirs(os.path.dirname(BLOCKLIST_FILE), exist_ok=True)

    if ip in _blocked:
        log.info(f"{ip} already blocked")
        return True

    _blocked.add(ip)

    # Write to file (pfSense can read this via alias URL)
    with open(BLOCKLIST_FILE, "a") as f:
        f.write(f"{ip}  # blocked {datetime.utcnow().isoformat()}\n")
    log.warning(f"Blocked {ip} — added to blocklist")

    # Optional: block via iptables on Linux
    _iptables_block(ip)

    return True


def _iptables_block(ip: str):
    """Block IP using iptables (Linux only)."""
    try:
        subprocess.run(
            ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
            check=True, capture_output=True
        )
        subprocess.run(
            ["iptables", "-A", "OUTPUT", "-d", ip, "-j", "DROP"],
            check=True, capture_output=True
        )
        log.info(f"iptables rule added for {ip}")
    except FileNotFoundError:
        log.info("iptables not available (Windows host) — file-only block")
    except subprocess.CalledProcessError as e:
        log.warning(f"iptables error: {e.stderr.decode()}")


def get_blocked_ips() -> list:
    if not os.path.exists(BLOCKLIST_FILE):
        return []
    with open(BLOCKLIST_FILE) as f:
        return [
            line.split()[0]
            for line in f
            if line.strip() and not line.startswith("#")
        ]


# ── pfSense API (uncomment if you have pfSense) ──────────────
# import requests
# PFSENSE_URL  = os.getenv("PFSENSE_URL", "https://192.168.1.1")
# PFSENSE_KEY  = os.getenv("PFSENSE_KEY", "")
# PFSENSE_SECRET = os.getenv("PFSENSE_SECRET", "")
#
# def block_ip_pfsense(ip: str):
#     resp = requests.post(
#         f"{PFSENSE_URL}/api/v1/firewall/alias/entry",
#         headers={"Authorization": f"{PFSENSE_KEY} {PFSENSE_SECRET}"},
#         json={"name": "SOC_BLOCKLIST", "address": ip},
#         verify=False
#     )
#     log.info(f"pfSense response: {resp.status_code}")
