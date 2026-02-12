# Deployment Guide

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
