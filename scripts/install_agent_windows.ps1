# scripts/install_agent_windows.ps1
# Run this on your Windows 10 VM as Administrator
# Replace WAZUH_MANAGER_IP with your Windows 11 host IP

param(
    [string]$ManagerIP = "192.168.100.1"  # Your Win11 host IP
)

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Wazuh Agent Installer — Windows 10 VM" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Manager IP: $ManagerIP"
Write-Host ""

# Download Wazuh Agent MSI
$msiUrl  = "https://packages.wazuh.com/4.x/windows/wazuh-agent-4.8.0-1.msi"
$msiPath = "$env:TEMP\wazuh-agent.msi"

Write-Host "[1/3] Downloading Wazuh Agent..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $msiUrl -OutFile $msiPath -UseBasicParsing
Write-Host "      Downloaded to $msiPath" -ForegroundColor Green

# Install silently with manager IP
Write-Host "[2/3] Installing Wazuh Agent..." -ForegroundColor Yellow
Start-Process msiexec.exe -ArgumentList `
    "/i `"$msiPath`" /qn WAZUH_MANAGER=`"$ManagerIP`" WAZUH_AGENT_NAME=`"Win10-VM`"" `
    -Wait -NoNewWindow
Write-Host "      Installation complete" -ForegroundColor Green

# Start the service
Write-Host "[3/3] Starting Wazuh Agent service..." -ForegroundColor Yellow
Start-Service -Name "WazuhSvc" -ErrorAction SilentlyContinue
Set-Service -Name "WazuhSvc" -StartupType Automatic
Write-Host "      Service started" -ForegroundColor Green

Write-Host ""
Write-Host "✅ Done! Agent should appear in Wazuh dashboard within 30s" -ForegroundColor Green
Write-Host "   Dashboard: https://$ManagerIP" -ForegroundColor Cyan
