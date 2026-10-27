$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$temp = Join-Path ([IO.Path]::GetTempPath()) "ouroboros-agent-gate-$([guid]::NewGuid())"
New-Item -ItemType Directory -Path $temp | Out-Null
$powershell = (Get-Command powershell.exe -ErrorAction Stop).Source
$originalPath = $env:Path

function Assert([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

try {
    $log = Join-Path $temp 'agent.log'
    $env:MOCK_LOG = $log
    $fakeCodex = Join-Path $temp 'codex.ps1'
    Set-Content -LiteralPath $fakeCodex -Encoding ascii -Value @'
param([Parameter(ValueFromRemainingArguments)][string[]]$Arguments)
Add-Content -LiteralPath $env:MOCK_LOG -Value (($Arguments -join ' ') + '|' + $env:MOCK_EXIT)
exit [int]$env:MOCK_EXIT
'@
    $env:Path = "$temp;$env:Path"

    $env:MOCK_EXIT = '0'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'scripts\run-agent-setup.ps1') -ProjectPath $root
    Assert -Condition ($LASTEXITCODE -eq 0) -Message 'PowerShell gate rejected a successful agent setup.'
    $call = Get-Content -Raw -LiteralPath $log
    $expectedCall = [regex]::Escape("exec --skip-git-repo-check -C $root ooo setup|0")
    Assert -Condition ($call -match $expectedCall) -Message 'PowerShell gate did not pass exactly `ooo setup` as the agent prompt.'

    $env:MOCK_EXIT = '23'
    $ErrorActionPreference = 'Continue'
    $stderr = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'scripts\run-agent-setup.ps1') -ProjectPath $root 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    Assert -Condition ($exitCode -eq 1) -Message 'PowerShell gate did not normalize setup failure to exit code 1.'
    Assert -Condition (($stderr | Out-String) -match 'No\s+further stack initialization was started') -Message 'PowerShell gate emitted no concrete stop message.'

    Remove-Item -LiteralPath $fakeCodex
    $env:Path = $temp
    $ErrorActionPreference = 'Continue'
    $stderr = & $powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'scripts\run-agent-setup.ps1') -ProjectPath $root 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    $env:Path = $originalPath
    Assert -Condition ($exitCode -eq 1) -Message 'PowerShell gate did not reject a missing agent with exit code 1.'
    $stderrText = $stderr | Out-String
    Assert -Condition ($stderrText -match 'Cannot start agent' -and $stderrText -match 'neither\s+Codex\s+nor\s+Claude\s+Code\s+is\s+available') -Message 'PowerShell gate emitted no concrete agent-start error.'

    $unixRoot = '/mnt/' + $root.Substring(0, 1).ToLowerInvariant() + $root.Substring(2).Replace('\', '/')
    & bash -c "bash '$unixRoot/tests/test-agent-setup-gate.sh'"
    Assert -Condition ($LASTEXITCODE -eq 0) -Message 'POSIX gate tests failed.'

    $psInstaller = Get-Content -Raw -LiteralPath (Join-Path $root 'scripts\install-stack.ps1')
    $shInstaller = Get-Content -Raw -LiteralPath (Join-Path $root 'scripts\install-stack.sh')
    foreach ($installer in $psInstaller,$shInstaller) {
        Assert -Condition ($installer.IndexOf('run-agent-setup') -gt $installer.IndexOf('uv tool install')) -Message 'Setup gate is not after the Ouroboros installation.'
        Assert -Condition ($installer.IndexOf('run-agent-setup') -gt $installer.IndexOf('ouroboros@ouroboros')) -Message 'Setup gate is not after the native Ouroboros plugin installation.'
        Assert -Condition ($installer.IndexOf('run-agent-setup') -lt $installer.IndexOf('npm install -g')) -Message 'Downstream initialization starts before the setup gate.'
        Assert -Condition ($installer -notmatch 'ouroboros setup --runtime') -Message 'Installer still bypasses the required agent action.'
        Assert -Condition ($installer.IndexOf('ui-ux-pro-max-cli@latest') -gt $installer.IndexOf('run-agent-setup')) -Message 'UI-UX-Pro-Max installation starts before the mandatory setup gate.'
        Assert -Condition ($installer.IndexOf('uipro init --ai codex') -gt $installer.IndexOf('ui-ux-pro-max-cli@latest')) -Message 'Codex UI-UX-Pro-Max initialization is missing or out of order.'
        Assert -Condition ($installer.IndexOf('max_iterations_per_ac') -gt $installer.IndexOf('run-agent-setup')) -Message 'Deep Path limits are configured before the mandatory setup gate.'
        Assert -Condition ($installer.IndexOf('max_iterations_per_ac') -lt $installer.IndexOf('ui-ux-pro-max-cli@latest')) -Message 'Deep Path limits are not configured immediately after setup.'
        foreach ($requiredSetting in 'max_iterations_per_ac','auto_evolve','stage3_enabled','generation_no_progress_timeout_seconds','generation_safety_timeout_seconds','verify_command_gate') {
            Assert -Condition ($installer.Contains($requiredSetting)) -Message "Deep Path setting missing: $requiredSetting"
        }
    }

    Write-Host 'Agent setup gate tests passed.'
} finally {
    $env:Path = $originalPath
    Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
}
