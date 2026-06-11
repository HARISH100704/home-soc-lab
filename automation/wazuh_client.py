"""
wazuh_client.py
Handles auth + queries to the Wazuh REST API.
"""

import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WAZUH_URL  = os.getenv("WAZUH_URL",  "https://localhost:55000")
WAZUH_USER = os.getenv("WAZUH_USER", "wazuh-wui")
WAZUH_PASS = os.getenv("API_PASSWORD", "")

_token: str = ""


def _get_token() -> str:
    global _token
    resp = requests.post(
        f"{WAZUH_URL}/security/user/authenticate",
        auth=(WAZUH_USER, WAZUH_PASS),
        verify=False
    )
    resp.raise_for_status()
    _token = resp.json()["data"]["token"]
    return _token


def _headers() -> dict:
    return {"Authorization": f"Bearer {_get_token()}"}


def get_recent_alerts(limit: int = 50, min_level: int = 10) -> list:
    """Fetch recent alerts with severity >= min_level."""
    params = {
        "limit": limit,
        "sort": "-timestamp",
        "q": f"rule.level>={min_level}"
    }
    resp = requests.get(
        f"{WAZUH_URL}/alerts",
        headers=_headers(),
        params=params,
        verify=False
    )
    resp.raise_for_status()
    return resp.json().get("data", {}).get("affected_items", [])


def get_agents() -> list:
    """List all enrolled Wazuh agents."""
    resp = requests.get(
        f"{WAZUH_URL}/agents",
        headers=_headers(),
        verify=False
    )
    resp.raise_for_status()
    return resp.json().get("data", {}).get("affected_items", [])
