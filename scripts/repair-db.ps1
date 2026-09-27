$ErrorActionPreference = "Stop"
Write-Host "Restarting LostLink backend and repairing/verifying the DB schema..." -ForegroundColor Cyan
docker compose -f infra/docker-compose.yml restart backend
Write-Host "Waiting for backend..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
docker compose -f infra/docker-compose.yml logs backend --tail=100
