$ErrorActionPreference = 'Stop'

function Test-OuroborosEndpoint {
    try {
        $body = '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
        $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8765/mcp' -Method Post -Headers @{ Accept = 'application/json, text/event-stream' } -ContentType 'application/json' -Body $body -TimeoutSec 3
        return $response.StatusCode -eq 200 -and $response.Content -match 'ouroboros_'
    } catch { return $false }
}

$listener = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    if (Test-OuroborosEndpoint) { exit 0 }
    throw 'Port 8765 is already used by a non-Ouroboros service.'
}

$command = Get-Command ouroboros -ErrorAction Stop
& $command.Source mcp serve --runtime codex --llm-backend codex --transport streamable-http --host 127.0.0.1 --port 8765 --idle-timeout 0
