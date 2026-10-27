[CmdletBinding()]
param([Parameter(Mandatory)][string]$ProjectPath)

$ErrorActionPreference = 'Stop'
$ProjectPath = [IO.Path]::GetFullPath($ProjectPath)

try {
    if (Get-Command codex -ErrorAction SilentlyContinue) {
        & codex exec --skip-git-repo-check -C $ProjectPath 'ooo setup'
    } elseif (Get-Command claude -ErrorAction SilentlyContinue) {
        & claude --print --permission-mode acceptEdits 'ooo setup'
    } else {
        [Console]::Error.WriteLine('ERROR: Cannot start agent for required first action `ooo setup`: neither Codex nor Claude Code is available.')
        exit 1
    }
} catch {
    [Console]::Error.WriteLine("ERROR: Could not start agent for required first action `ooo setup`: $($_.Exception.Message)")
    exit 1
}

if ($null -eq $LASTEXITCODE -or $LASTEXITCODE -ne 0) {
    $code = if ($null -eq $LASTEXITCODE) { 'unverified' } else { $LASTEXITCODE }
    [Console]::Error.WriteLine("ERROR: Required first agent action `ooo setup` did not complete successfully (exit code: $code). No further stack initialization was started.")
    exit 1
}
