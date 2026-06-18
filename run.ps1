param(
    [switch]$Install = $false
)

if ($Install) {
    Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
    pip install -r backend/requirements.txt -q

    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    cd frontend
    npm install
    cd ..

    Write-Host "Installation complete!" -ForegroundColor Green
    exit
}

Write-Host "Starting SQL Query Compiler & Security Analyzer..." -ForegroundColor Cyan
Write-Host ""

$backendJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir\backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8001
} -ArgumentList $PSScriptRoot

$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir\frontend
    npm run dev
} -ArgumentList $PSScriptRoot

Start-Sleep -Seconds 3

Write-Host "Backend API: http://localhost:8001" -ForegroundColor Green
Write-Host "Frontend App: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow

try {
    while ($true) {
        Start-Sleep -Seconds 1
        $bj = Receive-Job -Job $backendJob -ErrorAction SilentlyContinue
        $fj = Receive-Job -Job $frontendJob -ErrorAction SilentlyContinue
        if ($bj) { Write-Host $bj -ForegroundColor Red }
        if ($fj) { Write-Host $fj -ForegroundColor Red }
    }
}
finally {
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    Write-Host "Servers stopped." -ForegroundColor Green
}
