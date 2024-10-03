$f = "$PSScriptRoot/../scripts.d/50-svtav1.sh"
$c = Get-Content -Raw $f
$r = [regex]::Match($c, 'SCRIPT_REPO="(?<v>[^"]+)"').Groups['v'].Value
$sha = (git ls-remote --symref $r HEAD | Select-Object -Last 1) -split '\s+' | Select-Object -First 1
[IO.File]::WriteAllText($f, ($c -replace 'SCRIPT_COMMIT="[^"]*"', "SCRIPT_COMMIT=`"$sha`""))
Write-Host "svtav1 pinned to $sha"
