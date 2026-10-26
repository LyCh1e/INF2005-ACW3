# ACW3 lab runner — Windows.
# Rebuilds the images from the current source and (re)starts the target +
# backend containers defined in vulnerable-env\docker-compose.yml.
#
# Usage:
#   .\run.ps1              build (using cache) and start/recreate the lab
#   .\run.ps1 -NoCache     force a full rebuild with no Docker layer cache
#   .\run.ps1 -Down        stop and remove the containers

param(
    [switch]$NoCache,
    [switch]$Down
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvDir = Join-Path $ScriptDir "vulnerable-env"
$DigestFile = Join-Path $EnvDir "conf\digest.passwd"
$DigestUser = "labuser"
$DigestRealm = "acw3-dav"
$DigestPass = "labpass123"

function Invoke-Compose {
    param([string[]]$ComposeArgs)
    docker compose @ComposeArgs
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose $($ComposeArgs -join ' ') failed with exit code $LASTEXITCODE"
    }
}

Push-Location $EnvDir
try {
    if ($Down) {
        Write-Host "==> Stopping ACW3 lab"
        Invoke-Compose @("down")
        return
    }

    Write-Host "==> Checking Docker is running"
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker does not appear to be running. Start Docker Desktop and re-run this script."
        exit 1
    }

    if (-not (Test-Path $DigestFile)) {
        Write-Host "==> No digest.passwd found, creating default lab credentials ($DigestUser/$DigestPass)"
        New-Item -ItemType Directory -Force -Path (Join-Path $EnvDir "conf") | Out-Null
        $md5 = [System.Security.Cryptography.MD5]::Create()
        $bytes = [System.Text.Encoding]::UTF8.GetBytes("${DigestUser}:${DigestRealm}:${DigestPass}")
        $hashBytes = $md5.ComputeHash($bytes)
        $hash = -join ($hashBytes | ForEach-Object { $_.ToString("x2") })
        "${DigestUser}:${DigestRealm}:${hash}" | Out-File -FilePath $DigestFile -Encoding ascii -NoNewline
        Add-Content -Path $DigestFile -Value "" -Encoding ascii
    }

    Write-Host "==> Building images from the latest source"
    if ($NoCache) {
        Invoke-Compose @("build", "--no-cache")
    } else {
        Invoke-Compose @("build")
    }

    Write-Host "==> Starting the lab (recreating containers with the new images)"
    Invoke-Compose @("up", "-d", "--force-recreate")

    Write-Host "==> Containers:"
    Invoke-Compose @("ps")

    Write-Host ""
    Write-Host "ACW3 lab is up:"
    Write-Host "  Site:           http://localhost:8080/"
    Write-Host "  WebDAV (dav):   http://localhost:8080/dav/   (digest auth, see README for creds)"
    Write-Host "  Reverse proxy:  http://localhost:8080/proxy/"
    Write-Host "  CVE map:        http://localhost:8080/cve-map.html"
    Write-Host ""
    Write-Host "Tear down with:  .\run.ps1 -Down"
}
finally {
    Pop-Location
}
