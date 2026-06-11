# Incident Response Playbooks

## Playbook 1 — SSH Brute Force

**Trigger:** Wazuh rule 100001 fires (5+ SSH failures in 2 min)

**Steps:**
1. Engine enriches source IP via AbuseIPDB + OTX
2. If abuse score > 50 → auto-block IP
3. Telegram alert sent with attacker details
4. Check if any login succeeded (rule 100004) — if yes, escalate
5. Review auth.log on affected host for lateral movement

**Investigate:**
```bash
# On affected host — find all failed + successful logins from attacker IP
grep "ATTACKER_IP" /var/log/auth.log
# List currently logged-in users
who
last | head -20
```

---

## Playbook 2 — Port Scan Detected

**Trigger:** Suricata rule 9000001 fires

**Steps:**
1. Note scanning IP and time
2. Enrich IP — is it Shodan/Censys (internet background noise)?
3. If Greynoise marks as `noise=true` → low priority, log only
4. If targeted scan from unknown IP → notify + monitor for follow-on activity
5. Watch for exploitation attempts within next 10 minutes

---

## Playbook 3 — Reverse Shell / C2 Callback

**Trigger:** Suricata rule 9000021/9000022 fires (outbound to port 4444/1337)

**CRITICAL — High Priority**

**Steps:**
1. Immediately isolate affected host from network if possible
2. Identify process making the outbound connection
3. Capture the connection with Wireshark for analysis
4. Check VirusTotal for the process binary hash
5. Look for persistence mechanisms (new services, scheduled tasks, registry)

**On Windows (investigate):**
```powershell
# Find process making connection
netstat -bano | findstr "4444"
# Check for new scheduled tasks
schtasks /query /fo LIST /v | findstr "Task Name"
# Check startup entries
reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

---

## Playbook 4 — Successful Login After Brute Force

**Trigger:** Wazuh rule 100004 fires

**CRITICAL — Possible Compromise**

**Steps:**
1. Send immediate Telegram alert (already automatic)
2. Check what the attacker did after login
3. Look for new files, processes, cron jobs
4. Check if they moved laterally to other hosts
5. Consider isolating the compromised host
6. Change all passwords on the host

---

## Playbook 5 — File Integrity Alert

**Trigger:** Wazuh syscheck fires on critical path

**Steps:**
1. Identify which file changed and what changed
2. Was the change expected (update/patch)?
3. If unexpected — check who made the change and when
4. Verify binary hash against VirusTotal
5. If malicious → incident response for possible compromise
