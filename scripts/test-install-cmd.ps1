# Test: download + verify EXE (does not Start-Process)
$ReleaseUrl = "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe"
$e = Join-Path $env:TEMP "nazmul-test-download.exe"
Invoke-WebRequest -Uri $ReleaseUrl -OutFile $e -UseBasicParsing -TimeoutSec 120
$len = (Get-Item $e).Length
if ($len -lt 500000) { Write-Error "Too small: $len"; exit 1 }
Write-Host "OK: downloaded $([math]::Round($len/1MB,1)) MB to $e"
Remove-Item $e -Force
exit 0