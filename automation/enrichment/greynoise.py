"""enrichment/greynoise.py"""
import os
import requests

API_KEY = os.getenv("GREYNOISE_KEY", "")
BASE    = "https://api.greynoise.io/v3/community"


def check_greynoise(ip: str) -> dict:
    if not API_KEY:
        return {"noise": False, "riot": False, "error": "No key set"}
    try:
        resp = requests.get(
            f"{BASE}/{ip}",
            headers={"key": API_KEY},
            timeout=10
        )
        if resp.status_code == 404:
            return {"ip": ip, "noise": False, "riot": False, "classification": "unknown"}
        if resp.status_code != 200:
            return {"noise": False, "riot": False, "error": resp.status_code}
        data = resp.json()
        return {
            "ip":             ip,
            "noise":          data.get("noise", False),
            "riot":           data.get("riot", False),
            "classification": data.get("classification", "unknown"),
            "name":           data.get("name", "")
        }
    except Exception as e:
        return {"noise": False, "riot": False, "error": str(e)}
