<!--
Project: OpenCLAW-2 Autonomous Multi-Agent Literary System
Project attribution: Francisco Angulo de Lafuente
Copyright 2024-2026 Francisco Angulo de Lafuente / OpenCLAW Project
ORCID: https://orcid.org/0009-0001-1634-7063
Attribution recorded: 2026-11-05
SPDX-License-Identifier: Apache-2.0
-->

# Deployment Guide
> **Project attribution:** Francisco Angulo de Lafuente ([ORCID](https://orcid.org/0009-0001-1634-7063)). **Attribution recorded:** 2026-11-05. See [Cite and reuse](../README.md#cite-and-reuse).

## Local Development
```bash
python main.py --dry-run           # Test without posting
python main.py --task marketing    # Test single task
python main.py                     # Start 24/7 loop
```

## Docker
```bash
docker-compose up -d
docker-compose logs -f
```

## Render.com (Free Tier)
1. Connect your GitHub repo
2. Add environment variables in Render dashboard
3. Deploy as Background Worker (uses `render.yaml`)

## Railway
1. Connect GitHub repo
2. Add environment variables
3. Deploy (uses `railway.json`)

## Windows (PowerShell)
```powershell
cd E:\OpenCLAW-2
.\.venv\Scripts\activate
python main.py
```
