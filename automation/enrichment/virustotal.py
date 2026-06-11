"""enrichment/virustotal.py"""
import os
import requests

API_KEY = os.getenv("VIRUSTOTAL_KEY", "")
BASE    = "https://www.virustotal.com/api/v3"


def check_ip_virustotal(ip: str) -> dict:
    if not API_KEY:
        return {"error": "No VT key set"}
    try:
        resp = requests.get(
            f"{BASE}/ip_addresses/{ip}",
            headers={"x-apikey": API_KEY},
            timeout=10
        )
        if resp.status_code != 200:
            return {"error": resp.status_code}
        stats = resp.json()["data"]["attributes"]["last_analysis_stats"]
        return {
            "ip":         ip,
            "malicious":  stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless":   stats.get("harmless", 0),
            "verdict":    "MALICIOUS" if stats.get("malicious", 0) > 0 else "CLEAN"
        }
    except Exception as e:
        return {"error": str(e)}


def check_hash_virustotal(file_hash: str) -> dict:
    if not API_KEY:
        return {"error": "No VT key set"}
    try:
        resp = requests.get(
            f"{BASE}/files/{file_hash}",
            headers={"x-apikey": API_KEY},
            timeout=10
        )
        if resp.status_code != 200:
            return {"error": resp.status_code}
        attrs = resp.json()["data"]["attributes"]
        stats = attrs.get("last_analysis_stats", {})
        return {
            "hash":       file_hash,
            "name":       attrs.get("meaningful_name", "unknown"),
            "malicious":  stats.get("malicious", 0),
            "verdict":    "MALICIOUS" if stats.get("malicious", 0) > 0 else "CLEAN"
        }
    except Exception as e:
        return {"error": str(e)}
