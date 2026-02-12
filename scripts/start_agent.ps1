# OpenCLAW-2 Literary Agent — Windows Launch Script

Write-Host "🦅 Starting OpenCLAW-2 Literary Agent..." -ForegroundColor Cyan

# Activate virtual environment
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
}

# Launch
python main.py $args
