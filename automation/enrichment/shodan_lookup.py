"""enrichment/shodan_lookup.py"""
import os

API_KEY = os.getenv("SHODAN_KEY", "")


def get_shodan_info(ip: str) -> dict:
    if not API_KEY:
        return {"error": "No Shodan key set"}
    try:
        import shodan
        api  = shodan.Shodan(API_KEY)
        host = api.host(ip)
        return {
            "ip":         ip,
            "org":        host.get("org", "?"),
            "os":         host.get("os", "?"),
            "open_ports": [item["port"] for item in host.get("data", [])],
            "vulns":      list(host.get("vulns", {}).keys())
        }
    except Exception as e:
        return {"error": str(e)}
