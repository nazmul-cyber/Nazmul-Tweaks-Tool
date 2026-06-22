# Nazmul Tweaks Tool - Windows/Office Activation
# Multi-key + multi-KMS fallback (like classic Win10 activator)
# MAS option: https://github.com/massgravel/Microsoft-Activation-Scripts
param(
    [ValidateSet("status","windows","office","all","key","txt","mas")]
    [string]$Action = "all",
    [string]$ProductKey = ""
)

$ErrorActionPreference = "SilentlyContinue"
$Slmgr = "$env:SystemRoot\System32\slmgr.vbs"

function Write-Status {
    param([string]$msg, [string]$type = "info")
    $prefix = switch ($type) {
        "ok"   { "[OK]" }
        "err"  { "[ERR]" }
        "warn" { "[WARN]" }
        default { "[INFO]" }
    }
    Write-Host "$prefix $msg"
}

$keyFiles = @(
    "$PSScriptRoot\activation_keys.txt",
    "$PSScriptRoot\..\data\activation_keys.txt",
    "$env:LOCALAPPDATA\NazmulTweaksTool\data\activation_keys.txt"
)
$keyFile = $keyFiles | Where-Object { Test-Path $_ } | Select-Object -First 1

function Read-KeyDatabase {
    $db = @{
        Windows  = @{}
        AllKeys  = @()
        Office   = @{}
        KMSServers = @()
    }
    if (-not $keyFile) {
        Write-Status "Key file not found" "warn"
        return $db
    }
    $section = ""
    Get-Content $keyFile -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -match '^\[(.+)\]') {
            $section = $matches[1]
            return
        }
        if ($line -match '^#' -or $line -eq '') { return }
        if ($line -match '^([^=]+)=(.+)$') {
            $k = $matches[1].Trim()
            $v = $matches[2].Trim()
            if ($section -like "*Windows 10*" -or $section -like "*Windows 11*") {
                $db.Windows[$k] = $v
            }
            elseif ($section -like "*All Keys*") {
                if ($v -notin $db.AllKeys) { $db.AllKeys += $v }
            }
            elseif ($section -like "*Office*") {
                $db.Office[$k] = $v
            }
            elseif ($section -like "*KMS*") {
                if ($v -notin $db.KMSServers) { $db.KMSServers += $v }
            }
        }
    }
    if ($db.AllKeys.Count -eq 0) {
        $db.AllKeys = @($db.Windows.Values | Select-Object -Unique)
    }
    if ($db.KMSServers.Count -eq 0) {
        $db.KMSServers = @("kms.chinancce.com", "kms.shuax.com")
    }
    Write-Status "Loaded $($db.AllKeys.Count) keys, $($db.KMSServers.Count) KMS servers" "ok"
    return $db
}

function Get-WinStatus {
    $os = Get-CimInstance Win32_OperatingSystem
    $winAppId = "55C92734-D682-4D71-983E-D6EC3F16047F"
    $activeStatuses = @(1, 2, 3, 6)
    $licensed = "Not Activated"

    $products = Get-CimInstance SoftwareLicensingProduct -EA 0 |
        Where-Object {
            $_.PartialProductKey -and (
                $_.ApplicationId -eq $winAppId -or $_.Name -like "Windows*"
            )
        }
    if ($products | Where-Object { $_.LicenseStatus -in $activeStatuses }) {
        $licensed = "Activated"
    } else {
        $slmgr = "$env:SystemRoot\System32\slmgr.vbs"
        $dli = & cscript //nologo $slmgr /dli 2>&1 | Out-String
        if ($dli -match "(?i)license\s+status:\s*\**\s*licensed|permanently\s+activated") {
            $licensed = "Activated"
        }
    }

    return [PSCustomObject]@{
        Edition  = $os.Caption
        Build    = $os.BuildNumber
        Licensed = $licensed
    }
}

function Get-MatchingKey {
    param($db)
    $cap = (Get-CimInstance Win32_OperatingSystem).Caption
    if ($cap -match "11") { $ver = "Windows11" } else { $ver = "Windows10" }
    if ($cap -match "LTSB") {
        if ($cap -match "2016") { return $db.Windows["${ver}EnterpriseLTSB2016"] }
        return $db.Windows["${ver}EnterpriseLTSB2015"]
    }
    if ($cap -match "Enterprise") { return $db.Windows["${ver}Enterprise"] }
    if ($cap -match "Education")  { return $db.Windows["${ver}Education"] }
    if ($cap -match "Professional") { return $db.Windows["${ver}Pro"] }
    if ($cap -match "Pro")        { return $db.Windows["${ver}Pro"] }
    if ($cap -match "Home")       { return $db.Windows["${ver}Home"] }
    return $null
}

function Install-ProductKeys {
    param([string[]]$Keys)
    $installed = 0
    foreach ($key in $Keys) {
        if (-not $key) { continue }
        $out = & cscript //nologo $Slmgr /ipk $key 2>&1
        $text = ($out | Out-String).Trim()
        if ($text -match "successfully|installed") {
            Write-Status "Key installed: ...$($key.Split('-')[-1])" "ok"
            $installed++
        }
    }
    return $installed
}

function Try-KMSActivation {
    param([string[]]$Servers)
    foreach ($srv in $Servers) {
        Write-Status "Trying KMS server: $srv"
        & cscript //nologo $Slmgr /skms $srv 2>&1 | Out-Null
        Start-Sleep -Seconds 2
        $ato = & cscript //nologo $Slmgr /ato 2>&1
        $text = ($ato | Out-String)
        if ($text -match "successfully|activated") {
            Write-Status "KMS activation succeeded via $srv" "ok"
            return $true
        }
        $s = Get-WinStatus
        if ($s.Licensed -eq "Activated") {
            Write-Status "Windows ACTIVATED via $srv" "ok"
            return $true
        }
        Write-Status "Server $srv failed - trying next..." "warn"
    }
    return $false
}

function Activate-WindowsFromTxt {
    param($db)
    $status = Get-WinStatus
    Write-Status "Edition: $($status.Edition) | Build: $($status.Build)"
    if ($status.Licensed -eq "Activated") {
        Write-Status "Windows already activated" "ok"
        return $true
    }

    Write-Status "Windows activation starting (multi-key + KMS fallback)..."
    Restart-Service sppsvc -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    $keysToTry = [System.Collections.Generic.List[string]]::new()
    $match = Get-MatchingKey $db
    if ($match) { $keysToTry.Add($match) }
    foreach ($k in $db.AllKeys) {
        if ($k -notin $keysToTry) { $keysToTry.Add($k) }
    }

    Write-Status "Installing $($keysToTry.Count) product key(s)..."
    Install-ProductKeys -Keys $keysToTry.ToArray() | Out-Null
    Start-Sleep -Seconds 2

    $ok = Try-KMSActivation -Servers $db.KMSServers
    Start-Sleep -Seconds 2
    $final = Get-WinStatus
    if ($final.Licensed -eq "Activated") {
        Write-Status "Windows ACTIVATED - $($final.Edition)" "ok"
        return $true
    }
    if ($ok) {
        Write-Status "Activation attempted - reboot may be required" "warn"
    } else {
        Write-Status "All KMS servers failed - try MAS activator" "err"
    }
    return $false
}

function Activate-OfficeFromTxt {
    param($db)
    Write-Status "Activating Office..."
    $paths = @(
        "$env:ProgramFiles\Microsoft Office\Office16\OSPP.VBS",
        "${env:ProgramFiles(x86)}\Microsoft Office\Office16\OSPP.VBS"
    )
    $officeKey = $db.Office["Office2021ProPlus"]
    if (-not $officeKey) { $officeKey = $db.Office.Values | Select-Object -First 1 }
    $found = $false
    foreach ($p in $paths) {
        if (-not (Test-Path $p)) { continue }
        $found = $true
        if ($officeKey) {
            & cscript //nologo $p /inpkey:$officeKey 2>&1 | Out-Null
        }
        foreach ($srv in $db.KMSServers) {
            Write-Status "Office KMS: $srv"
            & cscript //nologo $p /sethst:$srv 2>&1 | Out-Null
            & cscript //nologo $p /act 2>&1 | Out-Null
            $out = & cscript //nologo $p /dstatus 2>&1
            if (($out | Out-String) -match "LICENSED") {
                Write-Status "Office ACTIVATED via $srv" "ok"
                return $true
            }
        }
        Write-Status "Office activation attempted" "warn"
    }
    if (-not $found) {
        Write-Status "Office not installed - skipped" "warn"
    }
    return $false
}

function Activate-WithKey {
    param([string]$key)
    if (-not $key) {
        Write-Status "No product key provided" "err"
        return
    }
    & cscript //nologo $Slmgr /ipk $key
    & cscript //nologo $Slmgr /ato
    Write-Status "Product key applied" "ok"
}

function Invoke-MASActivator {
    Write-Status "Opening MAS activator..."
    $masCmd = "irm https://get.activated.win | iex"
    Start-Process powershell -Verb RunAs -ArgumentList @(
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $masCmd
    )
    Write-Status "MAS opened - pick green option" "ok"
    return $true
}

Write-Host ""
Write-Host "  Nazmul Tweaks Tool - Activation Center"
Write-Host "  ========================================"
Write-Host ""

$db = Read-KeyDatabase

switch ($Action) {
    "status" {
        $w = Get-WinStatus
        Write-Status "Windows: $($w.Edition) | $($w.Licensed)"
    }
    "windows" { Activate-WindowsFromTxt $db | Out-Null }
    "office"  { Activate-OfficeFromTxt $db | Out-Null }
    "key"     { Activate-WithKey $ProductKey }
    "txt"     {
        Activate-WindowsFromTxt $db | Out-Null
        Activate-OfficeFromTxt $db | Out-Null
    }
    "mas"     { Invoke-MASActivator | Out-Null }
    "all"     {
        Activate-WindowsFromTxt $db | Out-Null
        Activate-OfficeFromTxt $db | Out-Null
        $w = Get-WinStatus
        if ($w.Licensed -eq "Activated") {
            Write-Status "Final: Windows is ACTIVATED" "ok"
        } else {
            Write-Status "Final: Windows not activated - try MAS button" "warn"
        }
    }
}
Write-Host ""