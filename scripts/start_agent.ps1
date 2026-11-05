# Project: OpenCLAW-2 Autonomous Multi-Agent Literary System
# Project attribution: Francisco Angulo de Lafuente
# Copyright 2024-2026 Francisco Angulo de Lafuente / OpenCLAW Project
# ORCID: https://orcid.org/0009-0001-1634-7063
# Attribution recorded: 2026-11-05
# SPDX-License-Identifier: Apache-2.0

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
