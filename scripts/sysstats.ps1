# CPU, RAM, GPU usage snapshot (JSON)
$ErrorActionPreference = "SilentlyContinue"

function Get-CpuPercent {
    try {
        $s1 = (Get-Counter '\Processor(_Total)\% Processor Time' -EA Stop).CounterSamples.CookedValue
        Start-Sleep -Milliseconds 120
        $s2 = (Get-Counter '\Processor(_Total)\% Processor Time' -EA Stop).CounterSamples.CookedValue
        return [math]::Round(($s1 + $s2) / 2)
    } catch {
        $load = Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average
        return [math]::Round($load.Average)
    }
}

function Get-RamStats {
    $os = Get-CimInstance Win32_OperatingSystem
    $total = [math]::Round($os.TotalVisibleMemorySize / 1024)
    $available = $total
    try {
        $available = [math]::Round((Get-Counter '\Memory\Available MBytes' -EA Stop).CounterSamples.CookedValue)
    } catch {
        $available = [math]::Round($os.FreePhysicalMemory / 1024)
    }
    $used = [math]::Max(0, $total - $available)
    $pct = if ($total -gt 0) { [math]::Round(100 * $used / $total) } else { 0 }
    return @{
        total_mb     = $total
        available_mb = $available
        free_mb      = $available
        used_mb      = $used
        used_pct     = $pct
    }
}

function Get-GpuPercent {
    try {
        $samples = (Get-Counter '\GPU Engine(*)\Utilization Percentage' -EA Stop).CounterSamples |
            Where-Object { $_.CookedValue -ge 0 -and $_.InstanceName -notmatch 'engtype_Copy' }
        if ($samples) {
            return [math]::Round(($samples | Measure-Object CookedValue -Maximum).Maximum)
        }
    } catch {}
    try {
        $nv = & nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>$null | Select-Object -First 1
        if ($nv -match '^\d+') { return [math]::Round([double]$nv) }
    } catch {}
    return 0
}

@{
    cpu_pct = Get-CpuPercent
    gpu_pct = Get-GpuPercent
    ram     = Get-RamStats
} | ConvertTo-Json -Compress -Depth 4