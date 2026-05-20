# Generate installer/manifest.xml with the production host URL.
# Usage:  .\build-manifest.ps1 -Host elom-max.github.io/augustine-citator
param(
    [Parameter(Mandatory=$true)]
    [string]$HostName
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$src = Join-Path $PSScriptRoot "..\manifest.xml"
$dst = Join-Path $PSScriptRoot "manifest.xml"

(Get-Content $src -Raw) -replace 'YOUR-DOMAIN\.example', $HostName | Set-Content $dst -NoNewline

Write-Host "Wrote installer/manifest.xml with host: https://$HostName"
