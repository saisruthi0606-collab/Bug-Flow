$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvActivate = Join-Path $root '.venv\Scripts\Activate.ps1'
if (-Not (Test-Path $venvActivate)) {
    Write-Error "Virtual environment not found at $venvActivate"
    exit 1
}
Write-Host "Activating virtual environment..."
. $venvActivate
Start-Process powershell -ArgumentList "-NoExit", "-Command cd '$root\backend'; uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command cd '$root\frontend'; npm run dev -- --host 0.0.0.0 --port 3000"
Start-Process "http://localhost:3000"
Write-Host "Started backend and frontend. Browser opened to http://localhost:3000"