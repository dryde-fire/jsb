# Ingest-Orchestrator.ps1
# Eseguito nightly da Office PC. Tenta Wake-on-LAN sul laptop (più veloce per E2B),
# fallback a esecuzione locale (qualità con E4B) se laptop non risponde.
#
# Legge config da %USERPROFILE%\.jsb-config.json, sezione "orchestrator".

param(
    [string]$ConfigPath = "$env:USERPROFILE\.jsb-config.json"
)

$ErrorActionPreference = "Continue"  # Vogliamo proseguire anche se WoL fallisce

# === Carica config ===
if (-not (Test-Path $ConfigPath)) {
    Write-Host "❌ Config not found: $ConfigPath" -ForegroundColor Red
    exit 1
}
$cfg = Get-Content $ConfigPath -Raw | ConvertFrom-Json

if ($cfg.role -ne "elaborator-quality") {
    Write-Host "⚠ This script is meant to run on the Office PC (role=elaborator-quality)." -ForegroundColor Yellow
    Write-Host "   Current role: $($cfg.role)" -ForegroundColor Gray
    Write-Host "   Continuing anyway..." -ForegroundColor Gray
}

if (-not $cfg.orchestrator) {
    Write-Host "❌ No 'orchestrator' section in config. This script only works on Office PC." -ForegroundColor Red
    exit 1
}

$LaptopIP = $cfg.orchestrator.laptop_ip
$LaptopMac = $cfg.orchestrator.laptop_mac
$LaptopVaultPath = $cfg.orchestrator.laptop_vault_path
$WakeTimeout = $cfg.orchestrator.laptop_wake_timeout_seconds
$FallbackLocal = $cfg.orchestrator.fallback_local_on_wake_failure

$LogFile = Join-Path $cfg.vault_path "_system\orchestrator-log.md"
$LogDir = Split-Path $LogFile
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Log-Msg {
    param([string]$Level, [string]$Msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [orchestrator] $Level`: $Msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

Log-Msg "INFO" "=== Orchestrator started ==="

# === Step 1: Tenta WoL ===
$laptopOnline = $false

# Primo check: già online?
$pingResult = Test-Connection -ComputerName $LaptopIP -Count 1 -Quiet -ErrorAction SilentlyContinue
if ($pingResult) {
    Log-Msg "INFO" "Laptop already online at $LaptopIP"
    $laptopOnline = $true
} else {
    Log-Msg "INFO" "Laptop offline. Sending magic packet to $LaptopMac..."

    # Magic packet manuale (no dependency esterna)
    try {
        $macBytes = $LaptopMac -replace '[:-]', '' -split '(..)' | Where-Object { $_ } | ForEach-Object { [byte]"0x$_" }
        $packet = (,[byte]0xFF * 6) + ($macBytes * 16)
        $udp = New-Object System.Net.Sockets.UdpClient
        $udp.Connect([System.Net.IPAddress]::Broadcast, 9)
        [void]$udp.Send($packet, $packet.Length)
        $udp.Close()
        Log-Msg "INFO" "Magic packet sent."
    } catch {
        Log-Msg "ERROR" "Failed to send magic packet: $_"
    }

    # Attendi che il laptop risponda
    $elapsed = 0
    $interval = 5
    while ($elapsed -lt $WakeTimeout) {
        Start-Sleep -Seconds $interval
        $elapsed += $interval
        if (Test-Connection -ComputerName $LaptopIP -Count 1 -Quiet -ErrorAction SilentlyContinue) {
            Log-Msg "INFO" "Laptop responded after ${elapsed}s"
            $laptopOnline = $true
            break
        }
    }

    if (-not $laptopOnline) {
        Log-Msg "WARN" "Laptop did not respond within ${WakeTimeout}s"
    }
}

# === Step 2: Esegui watchdog su laptop o localmente ===
if ($laptopOnline) {
    Log-Msg "INFO" "Executing watchdog on laptop via PSRemoting..."
    try {
        $session = New-PSSession -ComputerName $LaptopIP -ErrorAction Stop
        Invoke-Command -Session $session -ScriptBlock {
            param($vault)
            $watchdogPath = Join-Path $vault "_system\watchdog.py"
            python $watchdogPath
        } -ArgumentList $LaptopVaultPath
        Remove-PSSession $session
        Log-Msg "INFO" "✅ Laptop watchdog completed"
    } catch {
        Log-Msg "ERROR" "PSRemoting failed: $_"
        if ($FallbackLocal) {
            Log-Msg "WARN" "Falling back to local execution"
            $laptopOnline = $false
        } else {
            exit 1
        }
    }
}

if (-not $laptopOnline -and $FallbackLocal) {
    Log-Msg "INFO" "Executing watchdog locally (E4B quality fallback)..."
    $localWatchdog = Join-Path $cfg.vault_path "_system\watchdog.py"
    if (Test-Path $localWatchdog) {
        & python $localWatchdog
        Log-Msg "INFO" "✅ Local watchdog completed"
    } else {
        Log-Msg "ERROR" "Local watchdog not found at $localWatchdog"
        exit 1
    }
}

Log-Msg "INFO" "=== Orchestrator complete ==="
