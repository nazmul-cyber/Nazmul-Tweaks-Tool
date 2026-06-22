# Install Microsoft PC Manager - works for all users (winget + Store fallback)
$ErrorActionPreference = "Continue"

function Log($msg, $type) {
    $p = switch ($type) {
        "ok"   { "[OK]" }
        "err"  { "[ERR]" }
        "warn" { "[WARN]" }
        default { "[INFO]" }
    }
    Write-Host "$p $msg"
}

function Test-PCManagerInstalled {
    if (Get-AppxPackage -Name "*PCManager*" -ErrorAction SilentlyContinue) { return $true }
    $reg = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" -EA 0 |
        Where-Object { $_.DisplayName -match "PC Manager" }
    if ($reg) { return $true }
    $exe = Get-ChildItem "$env:ProgramFiles\WindowsApps" -Filter "PCManager.exe" -Recurse -EA 0 | Select-Object -First 1
    return [bool]$exe
}

function Test-WingetReady {
    try {
        $v = & winget -v 2>&1
        return ($LASTEXITCODE -eq 0 -or $v -match "\d")
    } catch { return $false }
}

function Test-WingetOutputFailed {
    param([string]$Text)
    $t = ($Text | Out-String).ToLower()
    return ($t -match "no package found" -or $t -match "no applicable" -or $t -match "not found matching")
}

function Invoke-WingetAttempt {
    param([string]$Label, [string[]]$Args)

    Log "Trying: $Label"
    $outFile = [System.IO.Path]::GetTempFileName()
    $errFile = [System.IO.Path]::GetTempFileName()
    try {
        $p = Start-Process -FilePath "winget" -ArgumentList $Args -Wait -PassThru -NoNewWindow `
            -RedirectStandardOutput $outFile -RedirectStandardError $errFile
        $stdout = Get-Content $outFile -Raw -EA 0
        $stderr = Get-Content $errFile -Raw -EA 0
        $combined = ($stdout + "`n" + $stderr).Trim()
        if ($combined) {
            foreach ($line in ($combined -split "`r?`n")) {
                $l = $line.Trim()
                if (-not $l) { continue }
                if ($l -match "^[\\\|\-/]+$" -or $l.Length -gt 80 -and $l -notmatch "\w") { continue }
                Write-Host "    $l"
            }
        }
        if (Test-WingetOutputFailed $combined) {
            Log "Not available via $Label on this PC" "warn"
            return $false
        }
        if ($p.ExitCode -eq 0 -or ($combined -match "already installed")) {
            Start-Sleep -Seconds 2
            if (Test-PCManagerInstalled) {
                Log "Microsoft PC Manager installed via $Label" "ok"
                return $true
            }
            Log "Install finished but PC Manager not detected yet — try the Store" "warn"
        }
    }
    finally {
        Remove-Item $outFile, $errFile -Force -EA 0
    }
    return $false
}

function Open-StorePCManager {
    Log "Opening Microsoft Store (click Install there)..." "info"
    Start-Process "ms-windows-store://pdp/?productid=9PM860492SZD"
    Log "Store page opened — click the blue Install button" "warn"
}

Log "Microsoft PC Manager setup..."

if (Test-PCManagerInstalled) {
    Log "Microsoft PC Manager already installed" "ok"
    Log "Open from Start Menu — search PC Manager" "info"
    exit 0
}

if (-not (Test-WingetReady)) {
    Log "winget missing — install App Installer from Microsoft Store" "warn"
    Start-Process "ms-windows-store://pdp/?productid=9NBLGGH4NNS1"
    Start-Sleep -Seconds 2
    Open-StorePCManager
    Log "PC Manager is NOT installed yet" "err"
    exit 1
}

Log "Updating winget sources (may take a moment)..."
Start-Process -FilePath "winget" -ArgumentList @("source", "update", "--disable-interactivity") -Wait -NoNewWindow | Out-Null

$attempts = @(
    @{ Label = "Microsoft Store app"; Args = @("install", "-e", "--id", "9PM860492SZD", "--source", "msstore", "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity") },
    @{ Label = "winget Microsoft.PCManager"; Args = @("install", "-e", "--id", "Microsoft.PCManager", "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity") },
    @{ Label = "winget by name"; Args = @("install", "--name", "Microsoft PC Manager", "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity") },
    @{ Label = "Store alt ID"; Args = @("install", "-e", "--id", "9NQ8LQPHF7VX", "--source", "msstore", "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity") }
)

foreach ($a in $attempts) {
    if (Invoke-WingetAttempt -Label $a.Label -Args $a.Args) { exit 0 }
    if (Test-PCManagerInstalled) {
        Log "Microsoft PC Manager detected after $($a.Label)" "ok"
        exit 0
    }
}

Open-StorePCManager
Log "Auto install failed — use one-click Install in the Store" "warn"
Log "PC Manager is NOT installed yet" "err"
exit 1