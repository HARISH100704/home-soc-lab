# Setup Guide — Home SOC Lab
## For: Windows 11 Host + Kali VM + Windows 10 VM

---

## Step 1 — VirtualBox Network Setup

Both VMs must be on the same **NAT Network** so they can talk to each other
and reach your Windows 11 host.

1. Open VirtualBox → `File → Tools → Network Manager`
2. Click **NAT Networks** tab → **Create**
3. Name it `SOCNet`, CIDR: `192.168.100.0/24`, enable DHCP
4. For **Kali VM**: Settings → Network → Adapter 1 → NAT Network → `SOCNet`
5. For **Win10 VM**: same — NAT Network → `SOCNet`
6. Your Win11 Host IP on this network will be `10.0.2.2` (VirtualBox default gateway)
   OR check with `ipconfig` on Win11 for your VirtualBox Host-Only adapter IP

---

## Step 2 — Install Docker Desktop on Windows 11

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Install and restart
3. Open Docker Desktop → Settings → Resources → set RAM to at least **4GB**
4. Open PowerShell as Administrator and test:
   ```
   docker --version
   docker-compose --version
   ```

---

## Step 3 — Clone and Configure

```powershell
# In PowerShell on Windows 11
git clone https://github.com/YOUR_USERNAME/home-soc-lab.git
cd home-soc-lab

# Copy env file and fill in your API keys
copy .env.example .env
notepad .env
```

Fill in:
- Your API keys (VirusTotal, AbuseIPDB, OTX, Greynoise, Shodan)
- Telegram bot token and chat ID
- Strong passwords for INDEXER_PASSWORD, DASHBOARD_PASSWORD, API_PASSWORD
- NETWORK_INTERFACE = your adapter name (run `ipconfig` to find it)

---

## Step 4 — Generate Wazuh SSL Certificates

```powershell
# Download the cert generation script from Wazuh
Invoke-WebRequest -Uri "https://packages.wazuh.com/4.8/config.yml" -OutFile config.yml
Invoke-WebRequest -Uri "https://packages.wazuh.com/4.8/wazuh-certs-tool.sh" -OutFile wazuh-certs-tool.sh

# Run in WSL or Linux — OR use the Docker-based approach:
docker run --rm -v ${PWD}/config:/tmp/wazuh wazuh/wazuh-certs-generator:0.0.1
```

> **Easier alternative**: Use the Wazuh all-in-one Docker deployment which handles certs automatically:
> https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html

---

## Step 5 — Start the Stack

```powershell
cd home-soc-lab
docker-compose up -d

# Watch startup (takes 2–3 minutes first time)
docker-compose logs -f
```

Check everything is running:
```powershell
docker-compose ps
```

You should see all containers as `Up`.

Access the dashboard: **https://localhost** (accept the self-signed cert warning)
- Username: `admin`
- Password: whatever you set as `INDEXER_PASSWORD`

---

## Step 6 — Install Wazuh Agent on Windows 10 VM

1. Copy `scripts/install_agent_windows.ps1` to your Win10 VM
2. Open PowerShell as Administrator on Win10
3. Run:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process
   .\install_agent_windows.ps1 -ManagerIP "YOUR_WIN11_HOST_IP"
   ```
4. Within 30 seconds, Win10 should appear in Wazuh dashboard under **Agents**

---

## Step 7 — Configure Suricata

Suricata needs to run on a machine that can see the network traffic.
On **Docker Desktop for Windows**, run Suricata in WSL2:

```bash
# In WSL2 terminal on Windows 11
sudo apt install suricata
sudo suricata-update   # Download Emerging Threats rules
sudo nano /etc/suricata/suricata.yaml
# Change: af-packet interface to eth0 (your WSL adapter)

sudo systemctl start suricata
sudo tail -f /var/log/suricata/fast.log  # Watch alerts live
```

Copy your custom rules:
```bash
sudo cp suricata/rules/custom.rules /var/lib/suricata/rules/
sudo suricata-update --no-reload
sudo kill -USR2 $(pidof suricata)  # Reload rules live
```

---

## Step 8 — Test Everything

From Kali VM, run the attack simulations:
```bash
chmod +x scripts/attack_simulations.sh
bash scripts/attack_simulations.sh 192.168.100.10   # Win10 VM IP
```

Watch in real time:
- **Kibana**: https://localhost → Security → Threat Hunting
- **Telegram**: You should get alerts on your phone
- **Suricata log**: `sudo tail -f /var/log/suricata/fast.log`

---

## Step 9 — Set Up Daily Threat Feed

```powershell
# On Windows 11, in Task Scheduler or just run manually:
cd home-soc-lab/automation
pip install -r requirements.txt
python threat_intel/feed_puller.py
```

Or in Docker (already runs via soc-engine service).

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Dashboard won't load | Wait 3–5 min for Elasticsearch to start; check `docker-compose logs wazuh.indexer` |
| Agent not connecting | Check Win11 firewall — allow ports 1514, 1515 inbound |
| No alerts in Kibana | Make sure Win10 agent shows "Active" in dashboard; check `docker-compose logs wazuh.manager` |
| Suricata no alerts | Verify interface name with `ip a`; check `suricata.yaml` interface setting |
| API key errors | Re-check `.env` — no quotes around values, no trailing spaces |
