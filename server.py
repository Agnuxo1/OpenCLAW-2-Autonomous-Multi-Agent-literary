"""
Health check server for cloud deployment (Render, Railway, etc.)
Runs alongside the main agent loop to satisfy hosting platform requirements.
"""

import asyncio
import threading
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime, timezone

app = FastAPI(title="OpenCLAW Literary Agent", version="2.0.0")

# Shared state for health reporting
_agent_status = {"started_at": datetime.now(timezone.utc).isoformat(), "heartbeats": 0}


def update_heartbeat():
    _agent_status["heartbeats"] += 1
    _agent_status["last_heartbeat"] = datetime.now(timezone.utc).isoformat()


@app.get("/")
async def root():
    return {"status": "running", "agent": "OpenCLAW Literary Agent v2.0", "info": _agent_status}


@app.get("/health")
async def health():
    return JSONResponse({"healthy": True, "uptime_heartbeats": _agent_status["heartbeats"]})


@app.get("/status")
async def status():
    return _agent_status


def start_health_server(host: str = "0.0.0.0", port: int = 8080):
    """Start health check server in background thread."""
    def run():
        uvicorn.run(app, host=host, port=port, log_level="warning")
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
