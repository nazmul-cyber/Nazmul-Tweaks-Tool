"""Windows tweak definitions — expanded & categorized."""

from dataclasses import dataclass


@dataclass
class Tweak:
    id: str
    name: str
    description: str
    category: str
    script: str
    icon: str = "⚙"
    recommended: bool = False


def _t(id, name, desc, cat, script, icon="⚙", rec=False):
    return Tweak(id, name, desc, cat, script.strip(), icon, rec)


PRTSC_SAFEGUARD_SCRIPT = r"""
    $path = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
    $current = (Get-ItemProperty -Path $path -Name "UsePrintScreenKeyForSnippingEnabled" -ErrorAction SilentlyContinue).UsePrintScreenKeyForSnippingEnabled
    if ($current -ne 1) {
        Set-ItemProperty -Path $path -Name "UsePrintScreenKeyForSnippingEnabled" -Value 1 -Type DWord -Force
        Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        Write-Host "[OK] Print Screen safeguard applied (Snipping Tool)"
    } else {
        Write-Host "[OK] Print Screen key protected"
    }
""".strip()


TWEAKS: list[Tweak] = [
    # Privacy
    _t("telemetry", "Disable Telemetry", "Stops Windows from sending diagnostic data.", "Privacy", r"""
        New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Force -EA 0 | Out-Null
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" AllowTelemetry 0 -Type DWord -Force
        Disable-ScheduledTask -TaskName "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser" -EA 0
        Disable-ScheduledTask -TaskName "\Microsoft\Windows\Application Experience\ProgramDataUpdater" -EA 0
        Write-Host "[OK] Telemetry disabled"
    """, "🔒", True),
    _t("activity", "Disable Activity History", "Stops tracking of app usage across devices.", "Privacy", r"""
        New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Force -EA 0 | Out-Null
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" PublishUserActivities 0 -Type DWord -Force
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy" TailoredExperiencesWithDiagnosticDataEnabled 0 -Type DWord -Force -EA 0
        Write-Host "[OK] Activity history disabled"
    """, "🔒", True),
    _t("ads_id", "Disable Advertising ID", "Blocks personalized ad tracking.", "Privacy", r"""
        New-Item -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" -Force | Out-Null
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" Enabled 0 -Type DWord -Force -ErrorAction Stop
        Write-Host "[OK] Advertising ID disabled"
    """, "🔒", True),
    _t("tips", "Disable Tips & Suggestions", "Removes tips, tricks, and suggested content.", "Privacy", r"""
        $cdm = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
        @("SubscribedContent-338389Enabled","SoftLandingEnabled","SilentInstalledAppsEnabled",
          "SubscribedContent-310093Enabled","SubscribedContent-338393Enabled") | ForEach-Object {
            Set-ItemProperty $cdm $_ 0 -Type DWord -Force -EA 0
        }
        Write-Host "[OK] Tips & suggestions disabled"
    """, "🔒", True),
    _t("location", "Disable Location Tracking", "Turns off location services.", "Privacy", r"""
        Set-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" Value "Deny" -Force -EA 0
        Write-Host "[OK] Location disabled"
    """, "🔒"),
    _t("cortana", "Disable Search Highlights", "Removes Bing search & highlights from Start.", "Privacy", r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" BingSearchEnabled 0 -Type DWord -Force -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" ShowDynamicSuggestions 0 -Type DWord -Force -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" CortanaConsent 0 -Type DWord -Force -EA 0
        Write-Host "[OK] Search highlights disabled"
    """, "🔒", True),
    _t("feedback", "Disable Feedback Notifications", "Stops Windows from asking for feedback.", "Privacy", r"""
        New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Force -EA 0 | Out-Null
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" DoNotShowFeedbackNotifications 1 -Type DWord -Force
        Write-Host "[OK] Feedback notifications disabled"
    """, "🔒"),

    # Performance
    _t("animations", "Disable UI Animations", "Makes Windows feel snappier.", "Performance", r"""
        Set-ItemProperty "HKCU:\Control Panel\Desktop\WindowMetrics" MinAnimate 0 -Force -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" ListviewAlphaSelect 0 -Type DWord -Force -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" VisualFXSetting 2 -Type DWord -Force -EA 0
        Write-Host "[OK] UI animations disabled"
    """, "⚡", True),
    _t("transparency", "Disable Transparency", "Turns off acrylic effects for better FPS.", "Performance", r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" EnableTransparency 0 -Type DWord -Force
        Write-Host "[OK] Transparency disabled"
    """, "⚡"),
    _t("sysmain", "Disable SysMain", "Recommended for SSDs — stops prefetch service.", "Performance", r"""
        Stop-Service SysMain -Force -EA 0; Set-Service SysMain -StartupType Disabled -EA 0
        Write-Host "[OK] SysMain disabled"
    """, "⚡", True),
    _t("power", "High Performance Plan", "Sets power plan to maximum performance.", "Performance", r"""
        powercfg /setactive SCHEME_MAX
        powercfg /change monitor-timeout-ac 0
        powercfg /change disk-timeout-ac 0
        Write-Host "[OK] High performance plan active"
    """, "⚡", True),
    _t("hibernate", "Disable Hibernation", "Frees disk space equal to your RAM.", "Performance", r"""
        powercfg /hibernate off
        Write-Host "[OK] Hibernation off — disk space freed"
    """, "⚡"),
    _t("faststartup", "Disable Fast Startup", "Fixes dual-boot & shutdown issues.", "Performance", r"""
        Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" HiberbootEnabled 0 -Type DWord -Force
        Write-Host "[OK] Fast startup disabled"
    """, "⚡"),
    _t("cleantemp", "Clean Temp Files", "Removes temporary files safely.", "Performance", r"""
        $n = 0; @($env:TEMP,"$env:LOCALAPPDATA\Temp","C:\Windows\Temp") | ForEach-Object {
            if (Test-Path $_) { Get-ChildItem $_ -Force -EA 0 | ForEach-Object {
                try { Remove-Item $_.FullName -Recurse -Force -EA Stop; $n++ } catch {}
            }}
        }; Write-Host "[OK] Cleaned $n temp items"
    """, "⚡", True),
    _t("searchidx", "Disable Search Indexing", "Reduces background CPU/disk on HDDs.", "Performance", r"""
        Stop-Service WSearch -Force -EA 0; Set-Service WSearch -StartupType Disabled -EA 0
        Write-Host "[OK] Windows Search indexing disabled"
    """, "⚡"),
    _t("startup_apps", "Disable Startup Apps", "Turns off programs in Task Manager > Startup.", "Performance", r"""
        $count = 0
        $disabled = [byte[]](0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00)
        foreach ($root in @(
            "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
            "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32",
            "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder"
        )) {
            if (-not (Test-Path $root)) { continue }
            $props = Get-ItemProperty -LiteralPath $root -ErrorAction SilentlyContinue
            if (-not $props) { continue }
            foreach ($name in $props.PSObject.Properties.Name) {
                if ($name -match '^PS') { continue }
                Set-ItemProperty -LiteralPath $root -Name $name -Value $disabled -Type Binary -Force -ErrorAction Stop
                $count++
            }
        }
        foreach ($folder in @(
            [Environment]::GetFolderPath('Startup'),
            "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
        )) {
            if (-not (Test-Path $folder)) { continue }
            Get-ChildItem -LiteralPath $folder -File -ErrorAction SilentlyContinue | ForEach-Object {
                $dest = "$($_.FullName).disabled"
                if (-not (Test-Path $dest)) {
                    Rename-Item -LiteralPath $_.FullName -NewName ($_.Name + ".disabled") -Force -ErrorAction Stop
                    $count++
                }
            }
        }
        Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {
            $_.State -eq 'Ready' -and $_.TaskPath -notmatch '\\Microsoft\\'
        } | ForEach-Object {
            $triggers = @($_.Triggers | Where-Object { $_.PSObject.TypeNames -match 'LogonTrigger' })
            if ($triggers.Count -gt 0) {
                Disable-ScheduledTask -TaskName $_.TaskName -TaskPath $_.TaskPath -ErrorAction SilentlyContinue | Out-Null
                $count++
            }
        }
        if ($count -gt 0) {
            Write-Host "[OK] Disabled $count startup entries — check Task Manager > Startup"
        } else {
            Write-Host "[OK] No extra startup entries found — already clean"
        }
    """, "🚀", True),

    # Explorer
    _t("extensions", "Show File Extensions", "Shows .txt .exe etc. in Explorer.", "Explorer", r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" HideFileExt 0 -Type DWord -Force
        Write-Host "[OK] File extensions visible"
    """, "📁", True),
    _t("hidden", "Show Hidden Files", "Shows hidden files and folders.", "Explorer", r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" Hidden 1 -Type DWord -Force
        Write-Host "[OK] Hidden files visible"
    """, "📁", True),
    _t("thispc", "Explorer Opens This PC", "Default location: This PC not Quick Access.", "Explorer", r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" LaunchTo 1 -Type DWord -Force
        Write-Host "[OK] Explorer opens to This PC"
    """, "📁", True),
    _t("recent", "Disable Recent Files", "Hides recent files in Quick Access.", "Explorer", r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer" ShowRecent 0 -Type DWord -Force
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer" ShowFrequent 0 -Type DWord -Force
        Write-Host "[OK] Recent files hidden"
    """, "📁"),
    _t("classic_menu", "Classic Right-Click (Win11)", "Full context menu on right-click.", "Explorer", r"""
        New-Item "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" -Force -EA 0 | Out-Null
        Set-ItemProperty "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" "(default)" "" -Force
        Stop-Process -Name explorer -Force -EA 0
        Write-Host "[OK] Classic context menu enabled"
    """, "📁"),
    _t("compact", "Disable Compact View", "Uses wider spacing in File Explorer.", "Explorer", r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" UseCompactMode 0 -Type DWord -Force -EA 0
        Write-Host "[OK] Compact view disabled"
    """, "📁"),

    # Debloat
    _t("xbox", "Disable Xbox Game Bar", "Removes Xbox overlay & background services.", "Debloat", r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" AppCaptureEnabled 0 -Type DWord -Force -EA 0
        New-Item "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" -Force -EA 0 | Out-Null
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" AllowGameDVR 0 -Type DWord -Force
        Get-AppxPackage *XboxGamingOverlay* | Remove-AppxPackage -EA 0
        Write-Host "[OK] Xbox Game Bar disabled"
    """, "🗑", True),
    _t("copilot", "Disable Copilot (Win11)", "Removes Copilot from taskbar.", "Debloat", r"""
        New-Item "HKCU:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" -Force -EA 0 | Out-Null
        Set-ItemProperty "HKCU:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" TurnOffWindowsCopilot 1 -Type DWord -Force
        Write-Host "[OK] Copilot disabled"
    """, "🗑", True),
    _t("consumer", "Disable Consumer Features", "Stops auto-install of promoted apps.", "Debloat", r"""
        New-Item "HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent" -Force -EA 0 | Out-Null
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent" DisableWindowsConsumerFeatures 1 -Type DWord -Force
        Write-Host "[OK] Consumer features disabled"
    """, "🗑", True),
    _t("widgets", "Disable Widgets (Win11)", "Removes Widgets panel from taskbar.", "Debloat", r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" TaskbarDa 0 -Type DWord -Force -EA 0
        Write-Host "[OK] Widgets disabled"
    """, "🗑"),
    _t("onedrive", "Hide OneDrive", "Removes OneDrive from Explorer sidebar.", "Debloat", r"""
        New-Item "HKLM:\SOFTWARE\Policies\Microsoft\Windows\OneDrive" -Force -EA 0 | Out-Null
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\OneDrive" DisableFileSyncNGSC 1 -Type DWord -Force -EA 0
        Write-Host "[OK] OneDrive hidden"
    """, "🗑"),
    _t("cortana_app", "Remove Cortana App", "Uninstalls Cortana UWP app.", "Debloat", r"""
        Get-AppxPackage *Cortana* | Remove-AppxPackage -EA 0
        Write-Host "[OK] Cortana app removed"
    """, "🗑"),

    # Updates
    _t("norestart", "No Auto-Restart Updates", "Prevents forced restart after updates.", "Updates", r"""
        New-Item "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Force -EA 0 | Out-Null
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" NoAutoRebootWithLoggedOnUsers 1 -Type DWord -Force
        Write-Host "[OK] Auto-restart disabled"
    """, "🔄", True),
    _t("delivery", "Disable Delivery Optimization", "Stops sharing updates with other PCs.", "Updates", r"""
        New-Item "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization" -Force -EA 0 | Out-Null
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization" DODownloadMode 0 -Type DWord -Force
        Write-Host "[OK] Delivery optimization disabled"
    """, "🔄"),
    _t("update_pause", "Pause Windows Updates", "Pauses feature updates for 1 year.", "Updates", r"""
        Set-ItemProperty "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings" FlightSettingsMaxPauseDays 365 -Type DWord -Force -EA 0
        Write-Host "[OK] Update pause configured (apply in Settings > Windows Update)"
    """, "🔄"),

    # Network
    _t("dns_cloudflare", "Cloudflare DNS", "Sets DNS to 1.1.1.1 for faster browsing.", "Network", r"""
        $a = Get-NetAdapter | Where-Object Status -eq "Up" | Select-Object -First 1
        if ($a) { Set-DnsClientServerAddress $a.InterfaceIndex -ServerAddresses ("1.1.1.1","1.0.0.1")
            Write-Host "[OK] Cloudflare DNS on $($a.Name)" } else { Write-Host "[OK] No active adapter — DNS unchanged" }
    """, "🌐"),
    _t("ipv6_off", "Disable IPv6", "Disables IPv6 on active adapters.", "Network", r"""
        Get-NetAdapter | Where-Object Status -eq "Up" | ForEach-Object {
            Disable-NetAdapterBinding $_.Name -ComponentID ms_tcpip6 -EA 0 }
        Write-Host "[OK] IPv6 disabled"
    """, "🌐"),
    _t("nodelay", "Disable Nagle Algorithm", "Can reduce network latency in games.", "Network", r"""
        Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces" -EA 0 | ForEach-Object {
            Set-ItemProperty $_.PSPath TcpAckFrequency 1 -Type DWord -Force -EA 0
            Set-ItemProperty $_.PSPath TCPNoDelay 1 -Type DWord -Force -EA 0
        }; Write-Host "[OK] Nagle algorithm disabled"
    """, "🌐"),

    # Gaming
    _t("prtsc_snip", "PrtSc Opens Screenshot Tool", "Print Screen key opens Win+Shift+S snipping tool.", "Explorer", PRTSC_SAFEGUARD_SCRIPT, "📸", True),
    _t("game_mode", "Enable Game Mode", "Prioritizes game performance.", "Gaming", r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\GameBar" AllowAutoGameMode 1 -Type DWord -Force -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\GameBar" AutoGameModeEnabled 1 -Type DWord -Force -EA 0
        Write-Host "[OK] Game Mode enabled"
    """, "🎮", True),
    _t("fullscreen_opt", "Disable Fullscreen Optimizations", "Better FPS in some games.", "Gaming", r"""
        Set-ItemProperty "HKCU:\SYSTEM\GameConfigStore" GameDVR_FSEBehaviorMode 2 -Type DWord -Force -EA 0
        Write-Host "[OK] Fullscreen optimizations disabled"
    """, "🎮"),
    _t("mouse_accel", "Disable Mouse Acceleration", "Raw 1:1 mouse input for gaming.", "Gaming", r"""
        Set-ItemProperty "HKCU:\Control Panel\Mouse" MouseSpeed 0 -Force
        Set-ItemProperty "HKCU:\Control Panel\Mouse" MouseThreshold1 0 -Force
        Set-ItemProperty "HKCU:\Control Panel\Mouse" MouseThreshold2 0 -Force
        Write-Host "[OK] Mouse acceleration disabled"
    """, "🎮", True),
]

UNDO_SCRIPTS: dict[str, str] = {
    "telemetry": r"""
        Remove-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" AllowTelemetry -EA 0
        Enable-ScheduledTask -TaskName "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser" -EA 0
        Enable-ScheduledTask -TaskName "\Microsoft\Windows\Application Experience\ProgramDataUpdater" -EA 0
        Write-Host "[OK] Telemetry settings reverted"
    """,
    "activity": r"""
        Remove-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" PublishUserActivities -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy" TailoredExperiencesWithDiagnosticDataEnabled 1 -Type DWord -Force -EA 0
        Write-Host "[OK] Activity history reverted"
    """,
    "ads_id": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" Enabled 1 -Type DWord -Force
        Write-Host "[OK] Advertising ID reverted"
    """,
    "tips": r"""
        $cdm = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
        @("SubscribedContent-338389Enabled","SoftLandingEnabled","SilentInstalledAppsEnabled",
          "SubscribedContent-310093Enabled","SubscribedContent-338393Enabled") | ForEach-Object {
            Set-ItemProperty $cdm $_ 1 -Type DWord -Force -EA 0
        }
        Write-Host "[OK] Tips & suggestions reverted"
    """,
    "location": r"""
        Set-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" Value "Allow" -Force -EA 0
        Write-Host "[OK] Location tracking reverted"
    """,
    "cortana": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" BingSearchEnabled 1 -Type DWord -Force -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" ShowDynamicSuggestions 1 -Type DWord -Force -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" CortanaConsent 1 -Type DWord -Force -EA 0
        Write-Host "[OK] Search highlights reverted"
    """,
    "feedback": r"""
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" DoNotShowFeedbackNotifications 0 -Type DWord -Force -EA 0
        Write-Host "[OK] Feedback notifications reverted"
    """,
    "animations": r"""
        Set-ItemProperty "HKCU:\Control Panel\Desktop\WindowMetrics" MinAnimate 1 -Force -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" ListviewAlphaSelect 1 -Type DWord -Force -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" VisualFXSetting 0 -Type DWord -Force -EA 0
        Write-Host "[OK] UI animations reverted"
    """,
    "transparency": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" EnableTransparency 1 -Type DWord -Force
        Write-Host "[OK] Transparency reverted"
    """,
    "sysmain": r"""
        Set-Service SysMain -StartupType Automatic -EA 0
        Start-Service SysMain -EA 0
        Write-Host "[OK] SysMain re-enabled"
    """,
    "power": r"""
        powercfg /setactive SCHEME_BALANCED
        Write-Host "[OK] Balanced power plan restored"
    """,
    "hibernate": r"""
        powercfg /hibernate on
        Write-Host "[OK] Hibernation re-enabled"
    """,
    "faststartup": r"""
        Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" HiberbootEnabled 1 -Type DWord -Force
        Write-Host "[OK] Fast startup re-enabled"
    """,
    "searchidx": r"""
        Set-Service WSearch -StartupType Automatic -EA 0
        Start-Service WSearch -EA 0
        Write-Host "[OK] Windows Search indexing re-enabled"
    """,
    "startup_apps": r"""
        $enabled = [byte[]](0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00)
        foreach ($root in @(
            "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
            "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32",
            "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder"
        )) {
            if (-not (Test-Path $root)) { continue }
            $props = Get-ItemProperty -LiteralPath $root -EA 0
            foreach ($name in $props.PSObject.Properties.Name) {
                if ($name -match '^PS') { continue }
                Set-ItemProperty -LiteralPath $root -Name $name -Value $enabled -Type Binary -Force -EA 0
            }
        }
        Get-ChildItem -Path "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp","$([Environment]::GetFolderPath('Startup'))" -Filter *.disabled -EA 0 |
            ForEach-Object { Rename-Item $_.FullName ($_.BaseName) -Force -EA 0 }
        Write-Host "[OK] Startup apps re-enabled (re-check Task Manager)"
    """,
    "extensions": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" HideFileExt 1 -Type DWord -Force
        Write-Host "[OK] File extensions hidden again"
    """,
    "hidden": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" Hidden 2 -Type DWord -Force
        Write-Host "[OK] Hidden files setting reverted"
    """,
    "thispc": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" LaunchTo 2 -Type DWord -Force
        Write-Host "[OK] Explorer default location reverted"
    """,
    "recent": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer" ShowRecent 1 -Type DWord -Force
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer" ShowFrequent 1 -Type DWord -Force
        Write-Host "[OK] Recent files re-enabled"
    """,
    "classic_menu": r"""
        Remove-Item "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" -Recurse -Force -EA 0
        Stop-Process -Name explorer -Force -EA 0
        Write-Host "[OK] Classic context menu reverted"
    """,
    "compact": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" UseCompactMode 1 -Type DWord -Force -EA 0
        Write-Host "[OK] Compact view re-enabled"
    """,
    "xbox": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" AppCaptureEnabled 1 -Type DWord -Force -EA 0
        Remove-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" AllowGameDVR -EA 0
        Write-Host "[OK] Xbox Game Bar settings reverted (reinstall app from Store if needed)"
    """,
    "copilot": r"""
        Remove-ItemProperty "HKCU:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" TurnOffWindowsCopilot -EA 0
        Write-Host "[OK] Copilot policy reverted"
    """,
    "consumer": r"""
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent" DisableWindowsConsumerFeatures 0 -Type DWord -Force -EA 0
        Write-Host "[OK] Consumer features reverted"
    """,
    "widgets": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" TaskbarDa 1 -Type DWord -Force -EA 0
        Write-Host "[OK] Widgets re-enabled"
    """,
    "onedrive": r"""
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\OneDrive" DisableFileSyncNGSC 0 -Type DWord -Force -EA 0
        Write-Host "[OK] OneDrive policy reverted"
    """,
    "norestart": r"""
        Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" NoAutoRebootWithLoggedOnUsers 0 -Type DWord -Force -EA 0
        Write-Host "[OK] Auto-restart policy reverted"
    """,
    "delivery": r"""
        Remove-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization" DODownloadMode -EA 0
        Write-Host "[OK] Delivery optimization reverted"
    """,
    "update_pause": r"""
        Remove-ItemProperty "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings" FlightSettingsMaxPauseDays -EA 0
        Write-Host "[OK] Update pause setting reverted"
    """,
    "dns_cloudflare": r"""
        Get-NetAdapter | Where-Object Status -eq "Up" | ForEach-Object {
            Set-DnsClientServerAddress $_.InterfaceIndex -ResetServerAddresses -EA 0
        }
        Write-Host "[OK] DNS reset to automatic"
    """,
    "ipv6_off": r"""
        Get-NetAdapter | Where-Object Status -eq "Up" | ForEach-Object {
            Enable-NetAdapterBinding $_.Name -ComponentID ms_tcpip6 -EA 0
        }
        Write-Host "[OK] IPv6 re-enabled"
    """,
    "nodelay": r"""
        Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces" -EA 0 | ForEach-Object {
            Remove-ItemProperty $_.PSPath TcpAckFrequency -EA 0
            Remove-ItemProperty $_.PSPath TCPNoDelay -EA 0
        }
        Write-Host "[OK] Nagle settings reverted"
    """,
    "prtsc_snip": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" UsePrintScreenKeyForSnippingEnabled 0 -Type DWord -Force -EA 0
        Write-Host "[OK] Print Screen key setting reverted"
    """,
    "game_mode": r"""
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\GameBar" AllowAutoGameMode 0 -Type DWord -Force -EA 0
        Set-ItemProperty "HKCU:\SOFTWARE\Microsoft\GameBar" AutoGameModeEnabled 0 -Type DWord -Force -EA 0
        Write-Host "[OK] Game Mode reverted"
    """,
    "fullscreen_opt": r"""
        Remove-ItemProperty "HKCU:\SYSTEM\GameConfigStore" GameDVR_FSEBehaviorMode -EA 0
        Write-Host "[OK] Fullscreen optimizations reverted"
    """,
    "mouse_accel": r"""
        Set-ItemProperty "HKCU:\Control Panel\Mouse" MouseSpeed 1 -Force
        Set-ItemProperty "HKCU:\Control Panel\Mouse" MouseThreshold1 6 -Force
        Set-ItemProperty "HKCU:\Control Panel\Mouse" MouseThreshold2 10 -Force
        Write-Host "[OK] Mouse acceleration restored"
    """,
}

NO_UNDO_IDS = frozenset({"cleantemp", "cortana_app"})


def get_undo_script(tweak_id: str) -> str | None:
    script = UNDO_SCRIPTS.get(tweak_id)
    return script.strip() if script else None


CATEGORIES = ["Privacy", "Performance", "Explorer", "Debloat", "Updates", "Network", "Gaming"]
FRESH_SETUP_IDS = [t.id for t in TWEAKS if t.recommended]

SPEED_UP_IDS = [
    "animations", "transparency", "sysmain", "power",
    "cleantemp", "searchidx", "faststartup", "startup_apps",
]

PRIVACY_BOOST_IDS = ["telemetry", "ads_id", "tips", "activity"]
GAMING_BOOST_IDS = ["game_mode", "mouse_accel", "fullscreen_opt", "nodelay"]
NETWORK_FIX_IDS = ["dns_cloudflare", "cleantemp"]