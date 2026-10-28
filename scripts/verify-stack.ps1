[CmdletBinding()]
param([string]$ProjectPath = (Get-Location).Path)
$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $python) { throw 'Python 3.10+ is required for the bundled setup checker.' }
& $python.Source (Join-Path $PSScriptRoot 'setup-runtime.py') --project ([IO.Path]::GetFullPath($ProjectPath))
if ($LASTEXITCODE) { throw 'Runtime checks failed; run the packaged /setup skill.' }
Write-Host 'Runtime checks passed; actual session CodeGraph MCP visibility must still be verified.'
