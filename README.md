# 🛡️ Home SOC Lab

> A functional Security Operations Center built on home hardware — real-time threat detection, log aggregation, SIEM dashboards, IDS/IPS, threat intelligence enrichment, and automated incident response.

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Wazuh](https://img.shields.io/badge/Wazuh-4.8-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Lab Setup

| Machine | Role |
|---------|------|
| Windows 11 Host | SOC Server — runs Docker (Wazuh + ELK) |
| Windows 10 VM | Victim — monitored via Wazuh Agent |
| Kali Linux VM | Attacker — runs simulated attacks |

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                 HOME NETWORK / NAT Network            │
│                                                      │
│  ┌─────────────┐         ┌──────────────────────┐   │
│  │  Kali Linux │────────▶│   Windows 10 VM      │   │
│  │  (Attacker) │  attack │   Wazuh Agent        │   │
│  └─────────────┘         └──────────┬───────────┘   │
│                                     │ logs           │
│                          ┌──────────▼───────────┐   │
│                          │  Windows 11 Host      │   │
│                          │                       │   │
│                          │  ┌─────────────────┐  │   │
│                          │  │  Wazuh Manager  │  │   │
│                          │  │  + ELK Stack    │  │   │
│                          │  │  + Suricata IDS │  │   │
│                          │  └────────┬────────┘  │   │
│                          │           │            │   │
│                          │  ┌────────▼────────┐  │   │
│                          │  │ Python SOC      │  │   │
│                          │  │ Engine          │  │   │
│                          │  │ (Enrichment +   │  │   │
│                          │  │  Auto-Response) │  │   │
│                          │  └─────────────────┘  │   │
│                          └───────────────────────┘   │
└──────────────────────────────────────────────────────┘
                                    │
                           📱 Telegram Alerts
```

---

## What It Detects

- Port scans and network reconnaissance (Nmap, Masscan)
- SSH / RDP brute force attacks
- Web application attacks (SQLi, XSS, directory traversal)
- Reverse shells and C2 callbacks
- DNS tunneling
- Privilege escalation (sudo, SUID, sudoers modification)
- File integrity violations on critical system paths
- Known malicious IPs via threat intelligence feeds

---

## Stack

| Layer | Tool |
|-------|------|
| SIEM | Wazuh 4.8 |
| Log Storage | Elasticsearch (Wazuh Indexer) |
| Dashboard | Kibana (Wazuh Dashboard) |
| Network IDS | Suricata + Emerging Threats Rules |
| Automation | Python 3.11 |
| Containers | Docker + Docker Compose |

---

## Threat Intelligence APIs

| API | Used For | Free Tier |
|-----|---------|-----------|
| [VirusTotal](https://www.virustotal.com/gui/join-us) | IP/hash reputation across 70+ AV engines | 500 req/day |
| [AbuseIPDB](https://www.abuseipdb.com/register) | Community IP abuse scoring | 1000 checks/day |
| [AlienVault OTX](https://otx.alienvault.com/api) | IOC pulses, threat actor context | Free |
| [Greynoise](https://www.greynoise.io/signup) | Filter background noise vs targeted attacks | Free (community) |
| [Shodan](https://account.shodan.io) | Open ports and CVEs on attacker IPs | Limited free |
| [Telegram Bot API](https://t.me/botfather) | Real-time push alerts to phone | Free |

---

## Automated Response Flow

```
High-Severity Alert (Wazuh Level ≥ 10)
          │
          ▼
   Enrich Source IP
   ┌──────────────────────────────┐
   │ VirusTotal + AbuseIPDB       │
   │ + OTX + Greynoise            │
   └──────────────┬───────────────┘
                  │
         Calculate Threat Score (0–100)
                  │
       ┌──────────┼──────────┐
       │          │          │
    < 30        30–79       ≥ 80
    LOG        NOTIFY     AUTO-BLOCK
    ONLY      Telegram    + Telegram
```

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/home-soc-lab.git
cd home-soc-lab

# 2. Add your API keys
cp .env.example .env
notepad .env   # or nano .env on Linux

# 3. Start all services
docker-compose up -d

# 4. Open dashboard (wait ~3 min for startup)
# https://localhost  (user: admin, pass: your INDEXER_PASSWORD)
```

Then install the Wazuh agent on your Windows 10 VM:
```powershell
# Run as Administrator on Win10 VM
.\scripts\install_agent_windows.ps1 -ManagerIP "YOUR_HOST_IP"
```

Then simulate attacks from Kali:
```bash
bash scripts/attack_simulations.sh <WIN10_VM_IP>
```

---

## Project Structure

```
home-soc-lab/
├── docker-compose.yml              # Full stack deployment
├── .env.example                    # API keys template
├── .gitignore
│
├── automation/
│   ├── soc_engine.py               # Main automation loop
│   ├── wazuh_client.py             # Wazuh REST API client
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── enrichment/
│   │   ├── virustotal.py
│   │   ├── abuseipdb.py
│   │   ├── otx.py
│   │   ├── greynoise.py
│   │   └── shodan_lookup.py
│   ├── response/
│   │   ├── notify.py               # Telegram alerts
│   │   └── block_ip.py             # iptables / blocklist
│   └── threat_intel/
│       └── feed_puller.py          # Daily OTX feed sync
│
├── wazuh/
│   └── rules/
│       ├── brute_force.xml         # Custom detection rules
│       └── c2_detection.xml
│
├── suricata/
│   ├── suricata.yaml
│   └── rules/
│       └── custom.rules            # Port scan, exploit, C2 rules
│
├── config/
│   └── wazuh_cluster/
│       └── wazuh_manager.conf
│
├── scripts/
│   ├── attack_simulations.sh       # Run from Kali to test detection
│   └── install_agent_windows.ps1   # Deploy agent on Win10 VM
│
└── docs/
    ├── setup_guide.md              # Step-by-step install guide
    └── playbooks.md                # Incident response procedures
```

---

## Docs

- [Full Setup Guide](docs/setup_guide.md) — step-by-step for Win11 + VirtualBox
- [Incident Response Playbooks](docs/playbooks.md) — what to do when alerts fire

---

## Resume Summary

> Built a home SOC lab replicating enterprise-grade security monitoring. Deployed Wazuh SIEM, Elasticsearch, Kibana, and Suricata IDS using Docker Compose on Windows 11, monitoring a Windows 10 VM via Wazuh agent. Developed a Python automation engine that enriches every alert using VirusTotal, AbuseIPDB, AlienVault OTX, and Greynoise APIs, calculates a composite threat score, and executes automated block/notify playbooks. Simulated real attacks from Kali Linux (port scans, brute force, Metasploit, web attacks) and validated end-to-end detection and alerting via Telegram.

**Stack:** Wazuh · Elasticsearch · Kibana · Suricata · Python · Docker · REST APIs · VirtualBox

---

## License

MIT — free to use, fork, and learn from.

> ⚠️ All attack simulations are performed only against your own lab VMs. Never run these against systems you don't own.
