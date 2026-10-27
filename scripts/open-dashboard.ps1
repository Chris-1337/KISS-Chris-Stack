[CmdletBinding()]
param(
    [Parameter(Mandatory)][uri]$Url,
    [switch]$DryRun,
    [switch]$NoOpen,
    [int]$ReadyTimeoutSec = 45
)

$ErrorActionPreference = 'Stop'
if ($Url.Scheme -notin 'http','https' -or $Url.Host -notin 'localhost','127.0.0.1','::1') {
    throw "Refusing non-loopback dashboard URL: $Url"
}

if ($DryRun) { Write-Output $Url.AbsoluteUri; exit 0 }

function Test-DashboardReady([uri]$Candidate, [int]$TimeoutSec) {
    $ApiUrl = [uri]::new($Candidate, '/api/runs')
    try {
        $Response = Invoke-WebRequest -UseBasicParsing -Uri $ApiUrl -TimeoutSec $TimeoutSec
        return $Response.StatusCode -eq 200 -and $Response.Content -match '"runs"\s*:'
    } catch { return $false }
}

$ResolvedUrl = $Url
if (-not (Test-DashboardReady $ResolvedUrl 3)) {
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw "Ouroboros dashboard URL is stale and uv is unavailable: $Url"
    }
    $UvTools = (& uv tool dir).Trim()
    $Python = @(
        (Join-Path $UvTools 'ouroboros-ai\Scripts\python.exe')
        (Join-Path $UvTools 'ouroboros-ai\bin\python')
    ) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $Python) { throw 'Ouroboros tool Python was not found.' }
    $BaseUrl = (& $Python -c 'from ouroboros.dashboard_web import dashboard_base_url; print(dashboard_base_url())' | Select-Object -Last 1).TrimEnd('/')
    if (-not $BaseUrl) { throw 'Ouroboros did not return a dashboard URL.' }
    $ResolvedUrl = [uri]($BaseUrl + $Url.Query)
}

$Deadline = [DateTime]::UtcNow.AddSeconds($ReadyTimeoutSec)
while (-not (Test-DashboardReady $ResolvedUrl 15)) {
    if ([DateTime]::UtcNow -ge $Deadline) {
        throw "Ouroboros dashboard run picker is not ready at $([uri]::new($ResolvedUrl, '/api/runs'))."
    }
    Start-Sleep -Milliseconds 250
}

if ($NoOpen) { Write-Output $ResolvedUrl.AbsoluteUri; exit 0 }
Start-Process $ResolvedUrl.AbsoluteUri
