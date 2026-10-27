$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$script = Join-Path $root 'scripts\open-dashboard.ps1'

$actual = & $script -Url 'http://localhost:54321/?run=exec_test' -DryRun
if ($actual -ne 'http://localhost:54321/?run=exec_test') { throw 'Loopback dashboard URL was not accepted.' }

$rejected = $false
try { & $script -Url 'https://example.com' -DryRun } catch { $rejected = $true }
if (-not $rejected) { throw 'Non-loopback dashboard URL was accepted.' }

if (Get-Command bash -ErrorAction SilentlyContinue) {
    $unixRoot = '/mnt/' + $root.Substring(0, 1).ToLowerInvariant() + $root.Substring(2).Replace('\', '/')
    $actual = & bash "$unixRoot/scripts/open-dashboard.sh" 'http://127.0.0.1:54321/?run=exec_test' --dry-run
    if ($LASTEXITCODE -ne 0 -or $actual -ne 'http://127.0.0.1:54321/?run=exec_test') { throw 'POSIX launcher rejected a loopback URL.' }
    $actual = & bash "$unixRoot/scripts/open-dashboard.sh" 'http://127.0.0.1:54321/?run=exec_test' --no-open --dry-run
    if ($LASTEXITCODE -ne 0 -or $actual -ne 'http://127.0.0.1:54321/?run=exec_test') { throw 'POSIX launcher option parsing failed.' }
    & bash "$unixRoot/scripts/open-dashboard.sh" 'https://example.com' --dry-run 2>$null
    if ($LASTEXITCODE -eq 0) { throw 'POSIX launcher accepted a non-loopback URL.' }
}

Write-Host 'Dashboard launcher tests passed.'
