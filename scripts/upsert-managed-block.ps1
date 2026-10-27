[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Path,
    [Parameter(Mandatory)][string]$PolicyPath
)

$ErrorActionPreference = 'Stop'
$begin = '<!-- kiss-chris-stack:start -->'
$end = '<!-- kiss-chris-stack:end -->'
$legacyBegin = '<!-- ouroboros-stack:start -->'
$legacyEnd = '<!-- ouroboros-stack:end -->'
$content = if (Test-Path -LiteralPath $Path) { [IO.File]::ReadAllText($Path) } else { '' }
$beginCount = ([regex]::Matches($content, [regex]::Escape($begin))).Count
$endCount = ([regex]::Matches($content, [regex]::Escape($end))).Count
$legacyBeginCount = ([regex]::Matches($content, [regex]::Escape($legacyBegin))).Count
$legacyEndCount = ([regex]::Matches($content, [regex]::Escape($legacyEnd))).Count
if ($beginCount -ne $endCount -or $legacyBeginCount -ne $legacyEndCount) { throw "Unmatched KISS-Chris-Stack marker in $Path" }
if ($beginCount -and $legacyBeginCount) { throw "Both current and legacy KISS-Chris-Stack blocks exist in $Path" }
if ($legacyBeginCount) {
    $content = $content.Replace($legacyBegin, $begin).Replace($legacyEnd, $end)
    $beginCount = $legacyBeginCount
}

$newline = if ($content -match "`r`n") { "`r`n" } else { "`n" }
$policy = ([IO.File]::ReadAllText($PolicyPath).Trim()).Replace("`r`n", "`n").Replace("`n", $newline)
$block = "$begin$newline$policy$newline$end"
if ($beginCount) {
    $pattern = "(?s)$([regex]::Escape($begin)).*?$([regex]::Escape($end))"
    $updated = [regex]::Replace($content, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $block })
} else {
    $separator = if (-not $content) { '' } elseif ($content.EndsWith($newline)) { $newline } else { "$newline$newline" }
    $updated = "$content$separator$block$newline"
}

$parent = Split-Path -Parent $Path
if ($parent) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
[IO.File]::WriteAllText($Path, $updated, [Text.UTF8Encoding]::new($false))
