# Nazmul Tweaks Tool - Windows, Office & Microsoft Apps status
$ErrorActionPreference = "SilentlyContinue"

function Get-WindowsLicense {
    $winAppId = "55C92734-D682-4D71-983E-D6EC3F16047F"
    $activeStatuses = @(1, 2, 3, 6)

    $products = Get-CimInstance SoftwareLicensingProduct -EA 0 |
        Where-Object {
            $_.PartialProductKey -and (
                $_.ApplicationId -eq $winAppId -or
                $_.Name -match "Windows|Operating System|Professional|Enterprise|Education|Workstation"
            )
        }
    if ($products | Where-Object { $_.LicenseStatus -in $activeStatuses }) { return "Activated" }

    $anyKey = Get-CimInstance SoftwareLicensingProduct -EA 0 |
        Where-Object { $_.PartialProductKey -and $_.LicenseStatus -in $activeStatuses }
    if ($anyKey | Where-Object { $_.Name -notmatch "Office" }) { return "Activated" }

    $slmgr = "$env:SystemRoot\System32\slmgr.vbs"
    $dli = & cscript //nologo $slmgr /dli 2>&1 | Out-String
    if ($dli -match "(?i)license\s+status:\s*\**\s*licensed") { return "Activated" }
    if ($dli -match "(?i)permanently\s+activated|windows\s+is\s+activated") { return "Activated" }

    $dlv = & cscript //nologo $slmgr /dlv 2>&1 | Out-String
    if ($dlv -match "(?i)license\s+status\s*=\s*licensed") { return "Activated" }
    if ($dlv -match "(?i)permanently\s+activated") { return "Activated" }

    $xpr = & cscript //nologo $slmgr /xpr 2>&1 | Out-String
    if ($xpr -match "(?i)permanently\s+activated|activated\s+successfully|will\s+expire") { return "Activated" }

    return "Not Activated"
}

function Find-OfficeOspp {
    $roots = @(
        "$env:ProgramFiles\Microsoft Office",
        ${env:ProgramFiles(x86)} + "\Microsoft Office"
    )
    foreach ($root in $roots) {
        if (-not (Test-Path $root)) { continue }
        $hit = Get-ChildItem -Path $root -Recurse -Filter "OSPP.VBS" -EA 0 | Select-Object -First 1
        if ($hit) { return $hit.FullName }
    }
    $static = @(
        "$env:ProgramFiles\Microsoft Office\Office16\OSPP.VBS",
        "${env:ProgramFiles(x86)}\Microsoft Office\Office16\OSPP.VBS",
        "$env:ProgramFiles\Microsoft Office\root\Office16\OSPP.VBS",
        "$env:ProgramFiles\Microsoft Office\root\vfs\ProgramFilesX86\Microsoft Office\Office16\OSPP.VBS",
        "$env:ProgramFiles\Microsoft Office\Office15\OSPP.VBS",
        "${env:ProgramFiles(x86)}\Microsoft Office\Office15\OSPP.VBS"
    )
    foreach ($p in $static) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

function Test-OhookOffice {
    $sysDll = "$env:SystemRoot\System32\sppc.dll"
    $sysSize = if (Test-Path $sysDll) { (Get-Item $sysDll).Length } else { 0 }

    $roots = @(
        "$env:ProgramFiles\Microsoft Office",
        ${env:ProgramFiles(x86)} + "\Microsoft Office"
    )
    foreach ($root in $roots) {
        if (-not (Test-Path $root)) { continue }
        if (Get-ChildItem -Path $root -Recurse -Filter "sppc.dll.backup" -EA 0 | Select-Object -First 1) {
            return $true
        }
        if ($sysSize -gt 0) {
            $custom = Get-ChildItem -Path $root -Recurse -Filter "sppc.dll" -EA 0 |
                Where-Object { $_.FullName -notmatch "\\Windows\\" } |
                Where-Object { $_.Length -gt 0 -and $_.Length -ne $sysSize } |
                Select-Object -First 1
            if ($custom) { return $true }
        }
    }
    return $false
}

function Get-OfficeProductName {
    $c2r = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Office\ClickToRun\Configuration" -EA 0
    if ($c2r.ProductReleaseIds) {
        return ($c2r.ProductReleaseIds -replace ",", ", ")
    }
    if ($c2r.ProductReleaseId) {
        return $c2r.ProductReleaseId
    }
    foreach ($rp in @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )) {
        $hit = Get-ItemProperty $rp -EA 0 |
            Where-Object { $_.DisplayName -match "Microsoft Office|Microsoft 365|Office 16|Office 21" } |
            Select-Object -First 1
        if ($hit) { return $hit.DisplayName }
    }
    return "Not detected"
}

function Test-OfficeInstalled {
    if (Find-OfficeOspp) { return $true }
    if (Test-Path "$env:ProgramFiles\Microsoft Office\root\Office16\WINWORD.EXE") { return $true }
    if (Test-Path "${env:ProgramFiles(x86)}\Microsoft Office\root\Office16\WINWORD.EXE") { return $true }
    $name = Get-OfficeProductName
    return ($name -ne "Not detected")
}

function Get-OfficeLicense {
    param([bool]$Installed)

    if (-not $Installed) { return "Not Installed" }

    $ospp = Find-OfficeOspp
    if ($ospp) {
        $out = & cscript //nologo $ospp /dstatus 2>&1 | Out-String
        if ($out -match "---LICENSED---") { return "Activated" }
        if ($out -match "LICENSE STATUS:\s*[-\s]*LICENSED") { return "Activated" }
        if ($out -match "Last 5 characters of installed product key:\s*\S+") { return "Activated" }
        if ($out -match "---OOB_GRACE---" -or $out -match "---NOTIFICATIONS---") { return "Activated" }
        if ($out -match "LICENSE STATUS:") { return "Not Activated" }
    }

    if (Test-OhookOffice) { return "Activated" }

    return "Not Activated"
}

function Get-OfficeInfo {
    $installed = Test-OfficeInstalled
    $product = Get-OfficeProductName
    if (-not $installed) {
        return @{
            product   = $product
            installed = "No"
            license   = "Not Installed"
        }
    }

    $ospp = Find-OfficeOspp
    if ($ospp) {
        $out = & cscript //nologo $ospp /dstatus 2>&1 | Out-String
        if ($out -match "PRODUCT NAME:\s*(.+)") {
            $product = $Matches[1].Trim()
        } elseif ($out -match "LICENSE NAME:\s*(.+)") {
            $product = $Matches[1].Trim()
        }
    }

    return @{
        product   = $product
        installed = "Yes"
        license   = (Get-OfficeLicense -Installed $true)
    }
}

function Test-MsApp {
    param([string]$Name, [scriptblock]$Check)
    $ok = [bool](& $Check)
    return @{ name = $Name; installed = $ok; status = if ($ok) { "Installed" } else { "Not Installed" } }
}

$os = Get-CimInstance Win32_OperatingSystem
$office = Get-OfficeInfo

$apps = @(
    (Test-MsApp "PC Manager" {
        if (Get-AppxPackage -Name "*PCManager*" -EA 0) { return $true }
        $reg = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
            "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" -EA 0 |
            Where-Object { $_.DisplayName -match "PC Manager" }
        return [bool]$reg
    })
    (Test-MsApp "Microsoft Edge" { Test-Path "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe" })
    (Test-MsApp "OneDrive" {
        (Test-Path "$env:LOCALAPPDATA\Microsoft\OneDrive\OneDrive.exe") -or (Get-AppxPackage -Name "*OneDrive*" -EA 0)
    })
    (Test-MsApp "Microsoft Store" { [bool](Get-AppxPackage -Name "Microsoft.WindowsStore" -EA 0) })
    (Test-MsApp "Teams" {
        [bool](Get-AppxPackage -Name "*Teams*" -EA 0) -or (Test-Path "$env:LOCALAPPDATA\Microsoft\Teams\current\Teams.exe")
    })
)

@{
    windows = @{
        edition = $os.Caption
        build   = "$($os.BuildNumber)"
        version = "$($os.Version)"
        license = (Get-WindowsLicense)
    }
    office  = $office
    apps    = $apps
} | ConvertTo-Json -Compress -Depth 5