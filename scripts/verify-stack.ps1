[CmdletBinding()]
param([string]$ProjectPath = (Get-Location).Path)

$ErrorActionPreference = 'Stop'
$failed = $false

function Check-Command([string]$Name) {
    if (Get-Command $Name -ErrorAction SilentlyContinue) {
        Write-Host "OK  $Name"
    } else {
        Write-Host "ERR $Name not found"
        $script:failed = $true
    }
}

'uv','ouroboros','ooo','codegraph','rtk','uipro' | ForEach-Object { Check-Command $_ }

if (Get-Command ouroboros -ErrorAction SilentlyContinue) {
    & ouroboros mcp doctor
    if ($LASTEXITCODE) { $failed = $true }
    $uvTools = (& uv tool dir).Trim()
    $ouroborosPython = @(
        (Join-Path $uvTools 'ouroboros-ai\Scripts\python.exe')
        (Join-Path $uvTools 'ouroboros-ai\bin\python')
    ) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $ouroborosPython) {
        Write-Host 'ERR Ouroboros tool Python missing'
        $failed = $true
    } else {
        & $ouroborosPython (Join-Path $PSScriptRoot 'patch-dashboard-picker.py') --check
        if ($LASTEXITCODE) { $failed = $true }
        & $ouroborosPython (Join-Path $PSScriptRoot 'verify-deep-path-config.py')
        if ($LASTEXITCODE) { $failed = $true }
        $dashboardUrl = (& $ouroborosPython -c 'from ouroboros.dashboard_web import dashboard_base_url; print(dashboard_base_url())' | Select-Object -Last 1).Trim()
        try {
            $runs = Invoke-RestMethod -Uri ([uri]::new([uri]$dashboardUrl, '/api/runs')) -TimeoutSec 5
            if ($null -eq $runs.runs) { throw 'runs field missing' }
            Write-Host "OK  Ouroboros dashboard run picker: $dashboardUrl"
        } catch {
            Write-Host "ERR Ouroboros dashboard run picker unavailable: $($_.Exception.Message)"
            $failed = $true
        }
    }
}
if (Get-Command codegraph -ErrorAction SilentlyContinue) {
    & codegraph status ([IO.Path]::GetFullPath($ProjectPath))
    if ($LASTEXITCODE) { $failed = $true }
}
if (Get-Command codex -ErrorAction SilentlyContinue) {
    $mcp = (& codex mcp list 2>&1 | Out-String)
    foreach ($name in 'ouroboros','codegraph') {
        if ($mcp -notmatch "(?m)^$name\s") { Write-Host "ERR Codex MCP missing: $name"; $failed = $true }
    }
    $task = Get-ScheduledTask -TaskName 'Ouroboros MCP' -ErrorAction SilentlyContinue
    if (-not $task) { Write-Host 'ERR Ouroboros MCP autostart task missing'; $failed = $true }
    elseif (($task.Actions.Execute -notmatch 'powershell') -or ($task.Actions.Arguments -notmatch 'start-ouroboros-mcp\.ps1')) {
        Write-Host 'ERR Ouroboros MCP autostart action is not managed by this stack'
        $failed = $true
    }
    $ready = $false
    for ($attempt = 0; $attempt -lt 10 -and -not $ready; $attempt++) {
        try {
            $body = '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
            $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8765/mcp' -Method Post -Headers @{ Accept = 'application/json, text/event-stream' } -ContentType 'application/json' -Body $body -TimeoutSec 3
            $ready = $response.StatusCode -eq 200 -and $response.Content -match 'ouroboros_'
        } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $ready) { Write-Host 'ERR Ouroboros MCP HTTP endpoint is not ready'; $failed = $true }
    $plugins = (& codex plugin list 2>&1 | Out-String)
    foreach ($name in 'ouroboros','ponytail') {
        if ($plugins -notmatch $name) { Write-Host "ERR Codex plugin missing: $name"; $failed = $true }
    }
    $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
    $agentsFile = Join-Path $codexHome 'AGENTS.md'
    if (-not (Test-Path -LiteralPath $agentsFile) -or (Get-Content -Raw $agentsFile) -notmatch 'meta\.job_observer' -or (Get-Content -Raw $agentsFile) -notmatch 'ui-ux-pro-max') {
        Write-Host 'ERR Codex global stack policy missing'
        $failed = $true
    }
    if (-not (Test-Path -LiteralPath (Join-Path $HOME '.agents\skills\ui-ux-pro-max\SKILL.md'))) {
        Write-Host 'ERR UI-UX-Pro-Max skill missing for Codex'
        $failed = $true
    }
}
if (Get-Command claude -ErrorAction SilentlyContinue) {
    $mcp = (& claude mcp list 2>&1 | Out-String)
    foreach ($name in 'ouroboros','codegraph') {
        if ($mcp -notmatch $name) { Write-Host "ERR Claude MCP missing: $name"; $failed = $true }
    }
    $plugins = (& claude plugin list 2>&1 | Out-String)
    foreach ($name in 'ouroboros','ponytail') {
        if ($plugins -notmatch $name) { Write-Host "ERR Claude plugin missing: $name"; $failed = $true }
    }
    $claudeHome = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' }
    if (-not (Test-Path -LiteralPath (Join-Path $claudeHome 'skills\ui-ux-pro-max\SKILL.md'))) {
        Write-Host 'ERR UI-UX-Pro-Max skill missing for Claude Code'
        $failed = $true
    }
}

$skill = Join-Path $HOME '.agents\skills\kiss-chris-stack\SKILL.md'
if (-not (Test-Path -LiteralPath $skill)) { Write-Host 'ERR KISS-Chris-Stack skill missing'; $failed = $true }

$mechanical = Join-Path ([IO.Path]::GetFullPath($ProjectPath)) '.ouroboros\mechanical.toml'
if (-not (Test-Path -LiteralPath $mechanical)) { Write-Host 'ERR Ouroboros mechanical gates missing'; $failed = $true }

$dashboardLauncher = Join-Path $HOME '.agents\skills\kiss-chris-stack\scripts\open-dashboard.ps1'
if (-not (Test-Path -LiteralPath $dashboardLauncher)) { Write-Host 'ERR Dashboard browser launcher missing'; $failed = $true }

if ($failed) { throw 'Stack verification failed.' }
Write-Host 'Stack verification passed.'
