# WWM Data Analysis - Application Launcher
# This script helps you launch the different components

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   WWM Data Analysis v1.2 - Application Launcher   " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "F:/Github/WWM Data Analysis/.venv/Scripts/Activate.ps1"

Write-Host ""
Write-Host "Select application to launch:" -ForegroundColor Green
Write-Host ""
Write-Host "  1. Data Extractor (Upload & extract match data)" -ForegroundColor White
Write-Host "     Port: 8502" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Main Dashboard (View statistics & analytics)" -ForegroundColor White
Write-Host "     Port: 8501" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Both Applications" -ForegroundColor White
Write-Host "     Extractor: 8502 | Dashboard: 8501" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting Data Extractor..." -ForegroundColor Green
        Write-Host "Access at: http://localhost:8502" -ForegroundColor Cyan
        streamlit run extractor.py --server.port=8502
    }
    "2" {
        Write-Host ""
        Write-Host "Starting Main Dashboard..." -ForegroundColor Green
        Write-Host "Access at: http://localhost:8501" -ForegroundColor Cyan
        streamlit run app.py --server.port=8501
    }
    "3" {
        Write-Host ""
        Write-Host "Starting both applications..." -ForegroundColor Green
        Write-Host "Data Extractor: http://localhost:8502" -ForegroundColor Cyan
        Write-Host "Main Dashboard: http://localhost:8501" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Press Ctrl+C to stop all applications" -ForegroundColor Yellow
        Write-Host ""
        
        # Start both in background
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; & '.\.venv\Scripts\Activate.ps1'; streamlit run extractor.py --server.port=8502"
        Start-Sleep -Seconds 2
        streamlit run app.py --server.port=8501
    }
    "4" {
        Write-Host ""
        Write-Host "Goodbye!" -ForegroundColor Green
        exit
    }
    default {
        Write-Host ""
        Write-Host "Invalid choice. Please run again." -ForegroundColor Red
    }
}
