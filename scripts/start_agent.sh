#!/bin/bash
# Project: OpenCLAW-2 Autonomous Multi-Agent Literary System
# Project attribution: Francisco Angulo de Lafuente
# Copyright 2024-2026 Francisco Angulo de Lafuente / OpenCLAW Project
# ORCID: https://orcid.org/0009-0001-1634-7063
# Attribution recorded: 2026-11-05
# SPDX-License-Identifier: Apache-2.0

# OpenCLAW-2 Literary Agent — Linux Launch Script

echo "🦅 Starting OpenCLAW-2 Literary Agent..."

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# Launch
python main.py "$@"
