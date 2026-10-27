$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$temp = Join-Path ([IO.Path]::GetTempPath()) "ouroboros-managed-config-$([guid]::NewGuid())"
New-Item -ItemType Directory -Path $temp | Out-Null

function Assert([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function Assert-ManagedUpdate([string]$File, [scriptblock]$Update, [string]$Newline = "`n") {
    $begin = '<!-- kiss-chris-stack:start -->'
    $end = '<!-- kiss-chris-stack:end -->'
    $legacyBegin = '<!-- ouroboros-stack:start -->'
    $legacyEnd = '<!-- ouroboros-stack:end -->'
    $foreignBefore = "# recipient settings${Newline}custom = keep${Newline}${Newline}"
    $foreignAfter = "${Newline}${Newline}# recipient footer${Newline}footer = keep${Newline}"
    [IO.File]::WriteAllText($File, "$foreignBefore$legacyBegin${Newline}stale policy${Newline}$legacyEnd$foreignAfter")
    & $Update
    $first = [IO.File]::ReadAllText($File)
    & $Update
    $second = [IO.File]::ReadAllText($File)
    Assert ($first -ceq $second) "$File is not idempotent."
    Assert ($first.StartsWith($foreignBefore)) "$File changed configuration before its managed block."
    Assert ($first.EndsWith($foreignAfter)) "$File changed configuration after its managed block."
    Assert (([regex]::Matches($first, [regex]::Escape($begin))).Count -eq 1) "$File does not contain exactly one managed block."
    Assert (-not $first.Contains($legacyBegin)) "$File retained the legacy managed block."
    Assert ($first.Contains('Before every implementation, formulate a strong `/goal`')) "$File did not install the current policy."
    Assert ($first.Contains('meta.job_observer')) "$File did not install host-owned observer startup."
    Assert ($first.Contains('ui-ux-pro-max')) "$File did not install UI-UX-Pro-Max routing."
    Assert ($first.Contains('ouroboros_start_execute_seed')) "$File did not install direct Seed routing."
    Assert ($first.Contains('three iterations per acceptance criterion')) "$File did not install bounded AC iterations."
    Assert ($first.Contains('auto_evolve')) "$File did not install bounded evolution policy."
}

try {
    $policy = Join-Path $root 'assets\global-stack-policy.md'
    $psFile = Join-Path $temp 'AGENTS.md'
    Assert-ManagedUpdate $psFile { & (Join-Path $root 'scripts\upsert-managed-block.ps1') -Path $psFile -PolicyPath $policy }

    $unixRoot = '/mnt/' + $root.Substring(0, 1).ToLowerInvariant() + $root.Substring(2).Replace('\', '/')
    $unixTemp = '/mnt/' + $temp.Substring(0, 1).ToLowerInvariant() + $temp.Substring(2).Replace('\', '/')
    $shFile = Join-Path $temp 'CLAUDE.md'
    Assert-ManagedUpdate $shFile { & bash "$unixRoot/scripts/upsert-managed-block.sh" "$unixTemp/CLAUDE.md" "$unixRoot/assets/global-stack-policy.md" } "`r`n"

    $textFiles = @(
        Get-Item (Join-Path $root 'README.md'),(Join-Path $root 'SKILL.md')
        Get-ChildItem -LiteralPath (Join-Path $root 'agents'),(Join-Path $root 'assets'),(Join-Path $root 'docs'),(Join-Path $root 'references'),(Join-Path $root 'scripts') -Recurse -File
    ) | Where-Object Extension -in '.md','.ps1','.sh','.yaml','.yml','.json','.toml'
    foreach ($file in $textFiles) {
        $content = Get-Content -Raw -LiteralPath $file.FullName
        Assert ($content -notmatch '(?i)(api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*["''][^$<{"'']+') "Possible hard-coded secret in $($file.FullName)."
        Assert ($content -notmatch '(?i)[A-Z]:\\Users\\[^$%<{\\]+|/home/[a-z0-9._-]+') "Non-portable user path in $($file.FullName)."
    }

    Write-Host 'Managed configuration tests passed.'
} finally {
    Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
}
