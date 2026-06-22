# Nazmul Tweaks Tool - System Refresh (RAM last = real recovery)
param([switch]$Elevated)

$ErrorActionPreference = "SilentlyContinue"

function Log($msg, $type) {
    $p = switch ($type) {
        "ok"   { "[OK]" }
        "warn" { "[WARN]" }
        default { "[INFO]" }
    }
    Write-Host "$p $msg"
}

function Test-IsAdmin {
    return ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Re-launch as Admin so RAM purge always has full rights (one UAC)
if (-not $Elevated -and -not (Test-IsAdmin)) {
    Log "Requesting Administrator for RAM recovery..." "info"
    $arg = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Elevated"
    try {
        $p = Start-Process -FilePath "powershell.exe" -Verb RunAs -Wait -WindowStyle Hidden -ArgumentList $arg -PassThru
        exit [math]::Max(0, $p.ExitCode)
    } catch {
        Log "UAC cancelled — RAM recovery will be very limited" "warn"
    }
}

$isAdmin = Test-IsAdmin

function Get-RamDetail {
    $os = Get-CimInstance Win32_OperatingSystem
    $total = [math]::Round($os.TotalVisibleMemorySize / 1024)
    $avail = $total
    try {
        $avail = [math]::Round((Get-Counter '\Memory\Available MBytes' -EA Stop).CounterSamples.CookedValue)
    } catch {
        $avail = [math]::Round($os.FreePhysicalMemory / 1024)
    }
    $used = [math]::Max(0, $total - $avail)
    $usedPct = if ($total -gt 0) { [math]::Round(100 * $used / $total) } else { 0 }
    $standby = 0
    $compressed = 0
    try {
        $standby = [math]::Round(
            (Get-Counter '\Memory\Standby Cache Normal Priority Bytes' -EA Stop).CounterSamples.CookedValue / 1MB
        )
    } catch {}
    try {
        $compressed = [math]::Round(
            (Get-Counter '\Memory\Compressed Bytes In Use' -EA Stop).CounterSamples.CookedValue / 1MB
        )
    } catch {}
    return @{
        ram_total_mb     = $total
        ram_available_mb = $avail
        ram_used_mb      = $used
        ram_used_pct     = $usedPct
        ram_standby_mb   = $standby
        ram_compressed_mb = $compressed
    }
}

function Get-Snapshot {
    $ram = Get-RamDetail
    $cpu = 0
    try {
        $cpu = [math]::Round((Get-Counter '\Processor(_Total)\% Processor Time' -EA Stop).CounterSamples.CookedValue)
    } catch {
        $cpu = [math]::Round((Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average)
    }
    $gpu = 0
    try {
        $gs = (Get-Counter '\GPU Engine(*)\Utilization Percentage' -EA Stop).CounterSamples |
            Where-Object { $_.CookedValue -ge 0 -and $_.InstanceName -notmatch 'engtype_Copy' } |
            ForEach-Object { $_.CookedValue }
        if ($gs) { $gpu = [math]::Round(($gs | Measure-Object -Maximum).Maximum) }
    } catch {}
    $ram.cpu_pct = $cpu
    $ram.gpu_pct = $gpu
    return $ram
}

function Enable-DebugPrivilege {
    $code = @'
using System;
using System.Runtime.InteropServices;
public static class NazmulPriv {
    [StructLayout(LayoutKind.Sequential)] struct LUID { public uint Low; public int High; }
    [StructLayout(LayoutKind.Sequential)] struct LUID_AND_ATTRIBUTES { public LUID Luid; public uint Attributes; }
    [StructLayout(LayoutKind.Sequential)] struct TOKEN_PRIVILEGES { public uint Count; public LUID_AND_ATTRIBUTES Privilege; }
    [DllImport("advapi32.dll", SetLastError=true)] static extern bool OpenProcessToken(IntPtr h, uint access, out IntPtr token);
    [DllImport("advapi32.dll", SetLastError=true, CharSet=CharSet.Unicode)] static extern bool LookupPrivilegeValue(string sys, string name, out LUID luid);
    [DllImport("advapi32.dll", SetLastError=true)] static extern bool AdjustTokenPrivileges(IntPtr token, bool disable, ref TOKEN_PRIVILEGES tp, int len, IntPtr prev, IntPtr ret);
    [DllImport("kernel32.dll")] static extern IntPtr GetCurrentProcess();
    public static void Enable(string name) {
        IntPtr tok;
        if (!OpenProcessToken(GetCurrentProcess(), 0x28, out tok)) return;
        LUID luid;
        if (!LookupPrivilegeValue(null, name, out luid)) return;
        var tp = new TOKEN_PRIVILEGES { Count = 1, Privilege = new LUID_AND_ATTRIBUTES { Luid = luid, Attributes = 2 } };
        AdjustTokenPrivileges(tok, false, ref tp, Marshal.SizeOf(tp), IntPtr.Zero, IntPtr.Zero);
    }
}
'@
    try {
        if (-not ("NazmulPriv" -as [type])) { Add-Type -TypeDefinition $code -Language CSharp -ErrorAction Stop }
        [NazmulPriv]::Enable("SeDebugPrivilege")
        [NazmulPriv]::Enable("SeProfileSingleProcessPrivilege")
        [NazmulPriv]::Enable("SeIncreaseQuotaPrivilege")
    } catch {}
}

function Clear-StandbyRam {
    $code = @'
using System;
using System.Runtime.InteropServices;
public static class NazmulStandby {
    [DllImport("ntdll.dll")] public static extern int NtSetSystemInformation(int InfoClass, ref int Info, int Length);
    public static int Purge(int cmd) { return NtSetSystemInformation(80, ref cmd, sizeof(int)); }
}
'@
    try {
        if (-not ("NazmulStandby" -as [type])) { Add-Type -TypeDefinition $code -Language CSharp -ErrorAction Stop }
        $freed = 0
        foreach ($cmd in 4, 5) {
            $c = $cmd
            if ([NazmulStandby]::Purge($c) -eq 0) { $freed++ }
        }
        return ($freed -gt 0)
    } catch { return $false }
}

function Invoke-WorkingSetTrim {
    $code = @'
using System;
using System.Runtime.InteropServices;
public static class NazmulTrim {
    [DllImport("kernel32.dll", SetLastError=true)] public static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
    [DllImport("kernel32.dll", SetLastError=true)] public static extern bool CloseHandle(IntPtr h);
    [DllImport("psapi.dll")] public static extern bool EmptyWorkingSet(IntPtr hProcess);
    const uint ACCESS = 0x001FFFFF;
    public static bool TrimPid(int pid) {
        IntPtr h = OpenProcess(ACCESS, false, pid);
        if (h == IntPtr.Zero) return false;
        bool ok = EmptyWorkingSet(h);
        CloseHandle(h);
        return ok;
    }
}
'@
    if (-not ("NazmulTrim" -as [type])) { Add-Type -TypeDefinition $code -Language CSharp -ErrorAction Stop }
    $protect = [System.Collections.Generic.HashSet[string]]::new(
        [string[]]@('Idle','System','Registry','smss','csrss','wininit','services','lsass','Memory Compression','Secure System','dwm','explorer'),
        [StringComparer]::OrdinalIgnoreCase
    )
    $n = 0
    Get-Process | ForEach-Object {
        if ($_.Id -le 4) { return }
        if ($protect.Contains($_.ProcessName)) { return }
        try { if ([NazmulTrim]::TrimPid($_.Id)) { $script:n++ } } catch {}
    }
    return $n
}

function Optimize-SystemMemory {
    param([hashtable]$Before)

    $before = $Before.ram_available_mb
    $beforePct = $Before.ram_used_pct
    $beforeStandby = $Before.ram_standby_mb

    Log "RAM optimize (final step — apps stay open)..." "info"
    Log "Before optimize: $beforePct% used | $before MB available | standby ~$beforeStandby MB" "info"

    if ($isAdmin) { Enable-DebugPrivilege }

    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
    [System.GC]::Collect()

    $totalTrim = 0
    foreach ($pass in 1..3) {
        $t = Invoke-WorkingSetTrim
        $totalTrim += $t
        Start-Sleep -Milliseconds 350
    }
    Log "Working-set trimmed on $totalTrim process touches (3 passes)" "ok"

    $purged = $false
    if ($isAdmin) {
        $purged = Clear-StandbyRam
        if ($purged) {
            Log "Standby cache purged" "ok"
        } else {
            Log "Standby purge API failed — trying fallback" "warn"
        }
    } else {
        Log "Not Admin — standby cache not purged" "warn"
    }

    if (-not $purged) {
        Start-Process "$env:SystemRoot\System32\rundll32.exe" "advapi32.dll,ProcessIdleTasks" -WindowStyle Hidden -Wait -EA 0 | Out-Null
    }

    # Final trim after purge
    Invoke-WorkingSetTrim | Out-Null
    Start-Sleep -Seconds 1

    $after = Get-RamDetail
    $gainMb = $after.ram_available_mb - $before
    $gainPct = $beforePct - $after.ram_used_pct
    $standbyDrop = $beforeStandby - $after.ram_standby_mb

    Log "After optimize: $($after.ram_used_pct)% used | $($after.ram_available_mb) MB available" "ok"
    if ($gainPct -gt 0) {
        Log "RAM usage dropped $gainPct% (+$gainMb MB available)" "ok"
    } elseif ($gainMb -gt 0) {
        Log "RAM available +$gainMb MB (usage % unchanged — apps re-allocated)" "info"
    } else {
        Log "Little/no RAM gain — close heavy apps (Chrome, games) for bigger drop" "warn"
    }
    if ($standbyDrop -gt 0) {
        Log "Standby cache reduced ~$standbyDrop MB" "ok"
    }

    return $after
}

function Refresh-WindowsGraphicsAndShell {
    Log "Refreshing Windows shell & graphics (fresh-boot feel)..." "info"

    $shellCode = @'
using System;
using System.Runtime.InteropServices;
public static class NazmulShell {
    [DllImport("shell32.dll")]
    public static extern void SHChangeNotify(uint eventId, uint flags, IntPtr item1, IntPtr item2);
    public static void RefreshDesktop() {
        SHChangeNotify(0x08000000, 0x0000, IntPtr.Zero, IntPtr.Zero);
        SHChangeNotify(0x8000000, 0x1000, IntPtr.Zero, IntPtr.Zero);
    }
}
'@
    try {
        if (-not ("NazmulShell" -as [type])) { Add-Type -TypeDefinition $shellCode -Language CSharp -ErrorAction Stop }
        [NazmulShell]::RefreshDesktop()
        Log "Desktop shell cache refreshed" "ok"
    } catch {
        Log "Shell notify skipped" "warn"
    }

    foreach ($proc in @('StartMenuExperienceHost', 'SearchHost', 'ShellExperienceHost', 'sihost')) {
        Get-Process -Name $proc -EA 0 | Stop-Process -Force -EA 0
    }
    Log "Windows UI helpers restarted (Start/Search/Taskbar)" "ok"
    Start-Sleep -Milliseconds 700

    foreach ($svc in @('Themes', 'UxSms', 'ShellHWDetection')) {
        try {
            Restart-Service -Name $svc -Force -EA Stop
            Log "Service restarted: $svc" "ok"
        } catch {}
    }

    Start-Process "rundll32.exe" -ArgumentList "user32.dll,UpdatePerUserSystemParameters" -WindowStyle Hidden -Wait -EA 0 | Out-Null
    Log "Display & visual parameters refreshed" "ok"

    Start-Process "ie4uinit.exe" -ArgumentList "-show" -WindowStyle Hidden -Wait -EA 0 | Out-Null
    Log "Icon cache refreshed" "ok"

    Log "Restarting Explorer (desktop shell)..."
    Stop-Process -Name explorer -Force -EA 0
    Start-Sleep -Seconds 2
    Start-Process explorer
    Log "Explorer restarted" "ok"

    Log "Refreshing GPU compositor (DWM)..."
    Stop-Process -Name dwm -Force -EA 0
    Start-Sleep -Seconds 2
    Log "Graphics compositor refreshed" "ok"
}

# ─── Main ───────────────────────────────────────────────────────────
$statsBefore = Get-Snapshot
Log "System Refresh starting..." "info"
Log "Before — RAM: $($statsBefore.ram_used_pct)% used ($($statsBefore.ram_available_mb) MB free) | CPU: $($statsBefore.cpu_pct)% | GPU: $($statsBefore.gpu_pct)%" "info"
if (-not $isAdmin) { Log "Run Launch Admin.bat if UAC was denied" "warn" }

Log "Flushing DNS..."
ipconfig /flushdns | Out-Null
Log "DNS flushed" "ok"

Log "Cleaning temp files..."
$n = 0
@($env:TEMP, "$env:LOCALAPPDATA\Temp", "C:\Windows\Temp") | ForEach-Object {
    if (Test-Path $_) {
        Get-ChildItem $_ -Force -EA 0 | ForEach-Object {
            try { Remove-Item $_.FullName -Recurse -Force -EA Stop; $n++ } catch {}
        }
    }
}
Log "Cleaned $n temp items" "ok"

Refresh-WindowsGraphicsAndShell

# RAM optimize LAST — shell/GPU refresh runs before we measure RAM gain
$statsAfterRam = Optimize-SystemMemory -Before $statsBefore
Start-Sleep -Milliseconds 800

$statsAfter = Get-Snapshot
$ramFreedMb = $statsAfter.ram_available_mb - $statsBefore.ram_available_mb
$ramDropPct = $statsBefore.ram_used_pct - $statsAfter.ram_used_pct
$cpuDrop = [math]::Max(0, $statsBefore.cpu_pct - $statsAfter.cpu_pct)
$gpuDrop = [math]::Max(0, $statsBefore.gpu_pct - $statsAfter.gpu_pct)

Log "After — RAM: $($statsAfter.ram_used_pct)% used ($($statsAfter.ram_available_mb) MB free) | CPU: $($statsAfter.cpu_pct)% | GPU: $($statsAfter.gpu_pct)%" "ok"
if ($ramDropPct -gt 0) {
    Log "Result: RAM $($statsBefore.ram_used_pct)% -> $($statsAfter.ram_used_pct)% (-$ramDropPct%)" "ok"
} elseif ($ramFreedMb -gt 0) {
    Log "Result: +$ramFreedMb MB available (usage % similar)" "ok"
} else {
    Log "Result: no measurable RAM drop — standby may already be low" "warn"
}

$statsJson = @{
    ram_before_available = $statsBefore.ram_available_mb
    ram_after_available  = $statsAfter.ram_available_mb
    ram_before_free      = $statsBefore.ram_available_mb
    ram_after_free       = $statsAfter.ram_available_mb
    ram_before_used_pct  = $statsBefore.ram_used_pct
    ram_after_used_pct   = $statsAfter.ram_used_pct
    ram_freed_mb         = $ramFreedMb
    ram_drop_pct         = [math]::Max(0, $ramDropPct)
    ram_total_mb         = $statsAfter.ram_total_mb
    ram_standby_before   = $statsBefore.ram_standby_mb
    ram_standby_after    = $statsAfter.ram_standby_mb
    cpu_before           = $statsBefore.cpu_pct
    cpu_after            = $statsAfter.cpu_pct
    cpu_freed_pct        = $cpuDrop
    gpu_before           = $statsBefore.gpu_pct
    gpu_after            = $statsAfter.gpu_pct
    gpu_freed_pct        = $gpuDrop
    is_admin             = $isAdmin
} | ConvertTo-Json -Compress

$statsFile = Join-Path $env:TEMP "nazmul_refresh_stats.json"
try { Set-Content -Path $statsFile -Value $statsJson -Encoding UTF8 -Force } catch {}

Write-Host "[STATS] $statsJson"
Log "System Refresh complete" "ok"
Write-Host ""