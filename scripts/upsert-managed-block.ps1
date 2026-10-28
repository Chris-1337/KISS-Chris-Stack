[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Path,
    [Parameter(Mandatory)][string]$PolicyPath
)

$ErrorActionPreference = 'Stop'
$begin = '<!-- kiss-chris-stack:start -->'
$end = '<!-- kiss-chris-stack:end -->'
$content = if (Test-Path -LiteralPath $Path) { [IO.File]::ReadAllText($Path) } else { '' }
$beginCount = ([regex]::Matches($content, [regex]::Escape($begin))).Count
$endCount = ([regex]::Matches($content, [regex]::Escape($end))).Count
if ($beginCount -ne $endCount) { throw "Unmatched KISS-Chris-Stack marker in $Path" }

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
