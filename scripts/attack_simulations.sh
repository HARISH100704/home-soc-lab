#!/bin/bash
# scripts/attack_simulations.sh
# Run these FROM Kali Linux AGAINST Win10 VM to test detection
# Usage: bash attack_simulations.sh <WIN10_IP>

TARGET=${1:-"192.168.100.10"}
echo "🎯 Target: $TARGET"
echo "⚠️  Only run this against your own lab VMs!"
echo ""

run_test() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "▶  TEST: $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ── 1. Port Scan ─────────────────────────────────────────────
run_test "Port Scan (nmap SYN scan)"
echo "Expected: Suricata SCAN rule fires, Wazuh alert"
nmap -sS -T4 -p 1-1000 $TARGET

# ── 2. Ping Sweep ────────────────────────────────────────────
run_test "Ping Sweep"
nmap -sn 192.168.100.0/24

# ── 3. SSH Brute Force ───────────────────────────────────────
run_test "SSH Brute Force (hydra)"
echo "Expected: Wazuh brute force rule fires, Telegram alert"
hydra -l administrator -P /usr/share/wordlists/rockyou.txt \
      ssh://$TARGET -t 4 -f -V 2>/dev/null | head -20

# ── 4. Web Scan ──────────────────────────────────────────────
run_test "Web Application Scan (nikto)"
echo "Expected: Suricata Nikto detection rule fires"
nikto -h http://$TARGET -maxtime 30

# ── 5. SMB Scan ──────────────────────────────────────────────
run_test "SMB Enumeration"
nmap -p 445 --script smb-enum-shares,smb-os-discovery $TARGET

# ── 6. DNS Queries (tunnel simulation) ──────────────────────
run_test "DNS Queries (tunnel simulation)"
for i in $(seq 1 10); do
    nslookup "aaaaabbbbbcccccdddddeeeeefffff${i}.example.com" > /dev/null 2>&1
done
echo "Sent 10 long DNS queries"

echo ""
echo "✅ Simulations complete — check Kibana dashboard"
echo "   http://HOST_IP:5601"
