# Quick test - does not run full install (stops before admin relaunch)
$u = 'https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/install.ps1'
$c = (Invoke-WebRequest -UseBasicParsing -Uri $u).Content
if ([string]::IsNullOrWhiteSpace($c)) { Write-Error 'EMPTY'; exit 1 }
Write-Host "OK: downloaded $($c.Length) chars"
if ($c -notmatch 'Nazmul Tweaks Tool Installer') { Write-Error 'BAD CONTENT'; exit 1 }
Write-Host "OK: valid installer script"
exit 0