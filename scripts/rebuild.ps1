$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
Write-Host "Stopping existing LostLink containers..." -ForegroundColor Yellow
docker compose -f infra/docker-compose.yml down
Write-Host "Rebuilding backend and frontend without stale layers..." -ForegroundColor Cyan
docker compose -f infra/docker-compose.yml build --no-cache backend frontend
Write-Host "Starting LostLink..." -ForegroundColor Green
docker compose -f infra/docker-compose.yml up
