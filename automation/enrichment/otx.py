"""enrichment/otx.py"""
import os
import requests

API_KEY = os.getenv("OTX_KEY", "")
BASE    = "https://otx.alienvault.com/api/v1"


def check_otx_ip(ip: str) -> dict:
    if not API_KEY:
        return {"pulse_count": 0, "error": "No key set"}
    try:
        resp = requests.get(
            f"{BASE}/indicators/IPv4/{ip}/general",
            headers={"X-OTX-API-KEY": API_KEY},
            timeout=10
        )
        if resp.status_code != 200:
            return {"pulse_count": 0, "error": resp.status_code}
        data   = resp.json()
        pulses = data.get("pulse_info", {}).get("pulses", [])
        return {
            "ip":           ip,
            "pulse_count":  len(pulses),
            "threat_names": [p["name"] for p in pulses[:5]],
            "verdict":      "KNOWN_THREAT" if pulses else "UNKNOWN"
        }
    except Exception as e:
        return {"pulse_count": 0, "error": str(e)}


def check_otx_domain(domain: str) -> dict:
    if not API_KEY:
        return {"pulse_count": 0, "error": "No key set"}
    try:
        resp = requests.get(
            f"{BASE}/indicators/domain/{domain}/general",
            headers={"X-OTX-API-KEY": API_KEY},
            timeout=10
        )
        if resp.status_code != 200:
            return {"pulse_count": 0, "error": resp.status_code}
        data   = resp.json()
        pulses = data.get("pulse_info", {}).get("pulses", [])
        return {
            "domain":       domain,
            "pulse_count":  len(pulses),
            "threat_names": [p["name"] for p in pulses[:5]]
        }
    except Exception as e:
        return {"pulse_count": 0, "error": str(e)}
