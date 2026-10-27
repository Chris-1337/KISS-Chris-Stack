[CmdletBinding()]
param(
    [string]$ProjectPath = (Get-Location).Path,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $PSScriptRoot
$ProjectPath = [IO.Path]::GetFullPath($ProjectPath)
$PolicyPath = Join-Path $Root 'assets\global-stack-policy.md'
$Package = 'ouroboros-ai[mcp,tui]'

function Say([string]$Message) { Write-Host $Message }
function Has-Command([string]$Name) { return [bool](Get-Command $Name -ErrorAction SilentlyContinue) }
function Run([scriptblock]$Action, [string]$Display) {
    Say "+ $Display"
    if (-not $DryRun) {
        $global:LASTEXITCODE = 0
        & $Action
        if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Display" }
    }
}
function Require([string]$Name) {
    if (-not (Has-Command $Name)) { throw "$Name is required." }
}

Require git
Require node
Require npm
Require npx

if (-not (Has-Command uv)) {
    Run {
        $installer = Join-Path ([IO.Path]::GetTempPath()) 'uv-install.ps1'
        Invoke-WebRequest 'https://astral.sh/uv/install.ps1' -OutFile $installer
        & powershell -NoProfile -ExecutionPolicy Bypass -File $installer
        Remove-Item -LiteralPath $installer -Force
    } 'install uv from astral.sh'
    $env:Path = "$(Join-Path $HOME '.local\bin');$env:Path"
}
if (-not $DryRun) { Require uv }

Run { uv tool install --force $Package } "uv tool install --force '$Package'"
$env:Path = "$(Join-Path $HOME '.local\bin');$env:Path"
if (-not $DryRun) { Require ouroboros }
if (-not $DryRun) { Require ooo }

if ($DryRun) {
    Say '+ apply/verify bounded Ouroboros dashboard picker hotfix'
} else {
    $UvTools = (& uv tool dir).Trim()
    $OuroborosPython = @(
        (Join-Path $UvTools 'ouroboros-ai\Scripts\python.exe')
        (Join-Path $UvTools 'ouroboros-ai\bin\python')
    ) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $OuroborosPython) { throw 'Ouroboros tool Python was not found.' }
    Run { & $OuroborosPython (Join-Path $Root 'scripts\patch-dashboard-picker.py') } 'apply/verify bounded Ouroboros dashboard picker hotfix'
}

function Install-Rtk {
    if ($env:PROCESSOR_ARCHITECTURE -notmatch 'AMD64|x86') {
        throw 'RTK currently publishes a native Windows x64 build only. Use WSL on Windows ARM.'
    }
    $release = Invoke-RestMethod 'https://api.github.com/repos/rtk-ai/rtk/releases/latest'
    $asset = $release.assets | Where-Object name -eq 'rtk-x86_64-pc-windows-msvc.zip' | Select-Object -First 1
    $checksumsAsset = $release.assets | Where-Object name -eq 'checksums.txt' | Select-Object -First 1
    if (-not $asset -or -not $checksumsAsset) { throw 'RTK Windows release or checksum asset not found.' }
    $tempDir = Join-Path ([IO.Path]::GetTempPath()) "kiss-chris-stack-rtk-$([guid]::NewGuid())"
    $archive = "$tempDir.zip"
    $checksums = "$tempDir-checksums.txt"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    try {
        Invoke-WebRequest $asset.browser_download_url -OutFile $archive
        Invoke-WebRequest $checksumsAsset.browser_download_url -OutFile $checksums
        $checksumLine = Get-Content -LiteralPath $checksums | Where-Object { $_ -match 'rtk-x86_64-pc-windows-msvc\.zip$' } | Select-Object -First 1
        if (-not $checksumLine) { throw 'RTK checksum entry not found.' }
        $expectedHash = ($checksumLine -split '\s+')[0].ToUpperInvariant()
        $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash
        if ($actualHash -ne $expectedHash) { throw 'RTK archive checksum mismatch.' }
        Expand-Archive -LiteralPath $archive -DestinationPath $tempDir -Force
        $binary = Get-ChildItem -LiteralPath $tempDir -Filter rtk.exe -Recurse | Select-Object -First 1
        if (-not $binary) { throw 'Downloaded RTK archive contains no rtk.exe.' }
        $binDir = Join-Path $HOME '.local\bin'
        New-Item -ItemType Directory -Path $binDir -Force | Out-Null
        Copy-Item -LiteralPath $binary.FullName -Destination (Join-Path $binDir 'rtk.exe') -Force
        $userPath = [string][Environment]::GetEnvironmentVariable('Path', 'User')
        if (($userPath -split ';') -notcontains $binDir) {
            [Environment]::SetEnvironmentVariable('Path', (($userPath.TrimEnd(';') + ";$binDir").TrimStart(';')), 'User')
        }
    } finally {
        Remove-Item -LiteralPath $tempDir,$archive,$checksums -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Run ${function:Install-Rtk} 'install/update RTK from the official GitHub release'
if (-not $DryRun) { Require rtk }

Run { npx -y github:JuliusBrussee/caveman } 'install/update Caveman for detected agents'

$HasCodex = Has-Command codex
$HasClaude = Has-Command claude

if ($HasCodex) {
    Run {
        & codex plugin marketplace add Q00/ouroboros 2>$null
        if ($LASTEXITCODE) { Say 'Ouroboros marketplace already present or could not be refreshed; continuing with verification.' }
        & codex plugin marketplace upgrade ouroboros 2>$null
        & codex plugin add ouroboros@ouroboros 2>$null
        & codex plugin marketplace add DietrichGebert/ponytail 2>$null
        if ($LASTEXITCODE) { Say 'Ponytail marketplace already present or could not be refreshed; continuing with verification.' }
        & codex plugin marketplace upgrade ponytail 2>$null
        & codex plugin add ponytail@ponytail 2>$null
        $plugins = (& codex plugin list 2>&1 | Out-String)
        if ($plugins -notmatch 'ouroboros' -or $plugins -notmatch 'ponytail') {
            throw 'Ouroboros or Ponytail plugin is not installed for Codex.'
        }
    } 'install/update Ouroboros and Ponytail plugins for Codex'
    Run { rtk init -g --codex } 'configure RTK for Codex'
}

if ($HasClaude) {
    Run {
        & claude plugin marketplace add Q00/ouroboros --scope user 2>$null
        & claude plugin install ouroboros@ouroboros --scope user 2>$null
        & claude plugin marketplace add DietrichGebert/ponytail --scope user 2>$null
        & claude plugin install ponytail@ponytail --scope user 2>$null
        $plugins = (& claude plugin list 2>&1 | Out-String)
        if ($plugins -notmatch 'ouroboros' -or $plugins -notmatch 'ponytail') {
            throw 'Ouroboros or Ponytail plugin is not installed for Claude Code.'
        }
    } 'install/update Ouroboros and Ponytail plugins for Claude Code'
    Run { rtk init -g --agent claude --auto-patch } 'configure RTK for Claude Code'
}

Say '+ run required first agent action: ooo setup'
if (-not $DryRun) {
    try {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root 'scripts\run-agent-setup.ps1') -ProjectPath $ProjectPath
    } catch {
        [Console]::Error.WriteLine("ERROR: Could not run required first agent action ``ooo setup``: $($_.Exception.Message). No further stack initialization was started.")
        exit 1
    }
    if ($LASTEXITCODE -ne 0) {
        [Console]::Error.WriteLine('ERROR: Required first agent action `ooo setup` was not verified successful. No further stack initialization was started.')
        exit 1
    }
}

$DeepPathSettings = [ordered]@{
    'clarification.max_interview_rounds' = '3'
    'execution.max_iterations_per_ac' = '3'
    'execution.auto_evolve' = 'false'
    'execution.auto_evolve_max_generations' = '1'
    'execution.verify_command_timeout_seconds' = '600'
    'evaluation.stage1_enabled' = 'true'
    'evaluation.stage2_enabled' = 'true'
    'evaluation.stage3_enabled' = 'false'
    'runtime_controls.generation_idle_timeout_seconds' = '600'
    'runtime_controls.generation_no_progress_timeout_seconds' = '900'
    'runtime_controls.generation_safety_timeout_seconds' = '3600'
    'orchestrator.default_max_turns' = '6'
    'seed.verify_command_gate' = 'block'
}
Run {
    foreach ($setting in $DeepPathSettings.GetEnumerator()) {
        & ouroboros config set $setting.Key $setting.Value
        if ($LASTEXITCODE -ne 0) { throw "Could not set Ouroboros configuration: $($setting.Key)" }
    }
    & ouroboros config validate
} 'configure bounded Ouroboros Deep Path'

Run { npm install -g 'ui-ux-pro-max-cli@latest' } 'install/update UI-UX-Pro-Max CLI'
if (-not $DryRun) { Require uipro }
if ($HasCodex) {
    Run {
        Push-Location $HOME
        try { & uipro init --ai codex } finally { Pop-Location }
    } 'initialize UI-UX-Pro-Max for Codex: uipro init --ai codex'
}
if ($HasClaude) {
    Run {
        Push-Location $HOME
        try { & uipro init --ai claude } finally { Pop-Location }
    } 'initialize UI-UX-Pro-Max for Claude Code: uipro init --ai claude'
}

Run { npm install -g '@colbymchenry/codegraph@latest' } 'npm install -g @colbymchenry/codegraph@latest'
if (-not $DryRun) { Require codegraph }

if (-not $HasCodex -and -not $HasClaude) {
    $fallbacks = [ordered]@{
        opencode = 'opencode'
        gemini = 'gemini'
        copilot = 'copilot'
        'kiro-cli' = 'kiro'
        pi = 'pi'
        hermes = 'hermes'
        goose = 'goose'
        omp = 'omp'
    }
    foreach ($entry in $fallbacks.GetEnumerator()) {
        if (Has-Command $entry.Key) {
            Run { npx -y skills@latest add DietrichGebert/ponytail --skill '*' -g -y --copy } 'install Ponytail skills for the detected agent'
            Run { npx -y skills@latest add $Root --skill kiss-chris-stack -g -y --copy } 'install KISS-Chris-Stack skill for the detected agent'
            break
        }
    }
}

Run { codegraph install --target=auto --location=global --yes } 'register CodeGraph MCP for detected agents'

if (Test-Path -LiteralPath (Join-Path $ProjectPath '.codegraph')) {
    Run { codegraph sync $ProjectPath } "update CodeGraph index: $ProjectPath"
} else {
    Run { codegraph init -i $ProjectPath } "initialize CodeGraph index: $ProjectPath"
}

$MechanicalPath = Join-Path $ProjectPath '.ouroboros\mechanical.toml'
if (Test-Path -LiteralPath $MechanicalPath) {
    Say "+ preserve mechanical gates: $MechanicalPath"
} else {
    Run { ooo detect $ProjectPath } "detect mechanical gates: $ProjectPath"
}

function Install-Skill([string]$SkillsRoot) {
    $legacyDestination = Join-Path $SkillsRoot 'ouroboros-stack'
    $destination = Join-Path $SkillsRoot 'kiss-chris-stack'
    Say "+ install skill: $destination"
    if ($DryRun) { return }
    if ((Test-Path -LiteralPath $legacyDestination) -and -not (Test-Path -LiteralPath $destination)) {
        Move-Item -LiteralPath $legacyDestination -Destination $destination
    }
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    foreach ($item in 'SKILL.md','README.md','agents','assets','docs','references','scripts') {
        Copy-Item -LiteralPath (Join-Path $Root $item) -Destination $destination -Recurse -Force
    }
}

$SharedSkillRoot = Join-Path $HOME '.agents\skills'
Install-Skill $SharedSkillRoot
if ($HasClaude) {
    $ClaudeHome = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' }
    Install-Skill (Join-Path $ClaudeHome 'skills')
}

function Upsert-MarkedBlock([string]$Path) {
    Say "+ update global instructions: $Path"
    if ($DryRun) { return }
    & (Join-Path $Root 'scripts\upsert-managed-block.ps1') -Path $Path -PolicyPath $PolicyPath
}

if ($HasCodex) {
    $CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
    Upsert-MarkedBlock (Join-Path $CodexHome 'AGENTS.md')
    $override = Join-Path $CodexHome 'AGENTS.override.md'
    if (Test-Path -LiteralPath $override) { Upsert-MarkedBlock $override }
}
if ($HasClaude) { Upsert-MarkedBlock (Join-Path $ClaudeHome 'CLAUDE.md') }

if ($HasCodex) {
    $installedScript = Join-Path $SharedSkillRoot 'kiss-chris-stack\scripts\start-ouroboros-mcp.ps1'
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$installedScript`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
    Run {
        Register-ScheduledTask -TaskName 'Ouroboros MCP' -Action $action -Trigger $trigger -Settings $settings -Description 'Starts the local Ouroboros MCP server for Codex on sign-in.' -Force | Out-Null
        Start-ScheduledTask -TaskName 'Ouroboros MCP'
    } 'register and start Ouroboros MCP user-logon task'
}

if (-not $DryRun) {
    & (Join-Path $Root 'scripts\verify-stack.ps1') -ProjectPath $ProjectPath
}
Say 'Done. Restart the agent so plugins, hooks, MCP servers, and global instructions reload.'
