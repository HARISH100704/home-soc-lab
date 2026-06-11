"""enrichment/abuseipdb.py"""
import os
import requests

API_KEY = os.getenv("ABUSEIPDB_KEY", "")
BASE    = "https://api.abuseipdb.com/api/v2"


def check_abuseipdb(ip: str) -> dict:
    if not API_KEY:
        return {"abuse_score": 0, "error": "No key set"}
    try:
        resp = requests.get(
            f"{BASE}/check",
            headers={"Key": API_KEY, "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90},
            timeout=10
        )
        if resp.status_code != 200:
            return {"abuse_score": 0, "error": resp.status_code}
        d = resp.json()["data"]
        return {
            "ip":            ip,
            "abuse_score":   d.get("abuseConfidenceScore", 0),
            "country":       d.get("countryCode", "?"),
            "isp":           d.get("isp", "?"),
            "total_reports": d.get("totalReports", 0),
            "is_tor":        d.get("isTor", False)
        }
    except Exception as e:
        return {"abuse_score": 0, "error": str(e)}
