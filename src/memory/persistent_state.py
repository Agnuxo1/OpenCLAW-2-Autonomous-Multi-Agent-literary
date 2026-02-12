"""
Persistent State Management
============================
Local JSON + optional remote GitHub Gist backup.
Tracks all agent activities, metrics, and learned strategies.
"""

import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
import aiofiles
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PersistentState:
    """Manages agent state with local + remote persistence."""

    def __init__(self, state_dir: str, github_pat: str = "", gist_id: str = ""):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.github_pat = github_pat
        self.gist_id = gist_id
        self._state: Dict[str, Any] = {}
        self._dirty = False

    async def load(self):
        """Load state from disk."""
        state_file = self.state_dir / "agent_state.json"
        if state_file.exists():
            async with aiofiles.open(state_file, "r") as f:
                self._state = json.loads(await f.read())
            logger.info(f"State loaded: {len(self._state)} keys")
        else:
            self._state = self._default_state()
            await self.save()
            logger.info("Fresh state initialized")

    def _default_state(self) -> Dict[str, Any]:
        return {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_heartbeat": None,
            "total_heartbeats": 0,
            "metrics": {
                "posts_created": 0,
                "emails_sent": 0,
                "submissions_made": 0,
                "forum_comments": 0,
                "library_requests": 0,
                "total_llm_calls": 0,
            },
            "task_history": [],
            "active_campaigns": [],
            "submission_tracker": [],
            "learned_strategies": [],
            "platform_accounts": {},
            "content_log": [],
            "errors": [],
            "daily_summaries": [],
        }

    async def save(self):
        """Persist state to disk and optionally to GitHub Gist."""
        state_file = self.state_dir / "agent_state.json"
        async with aiofiles.open(state_file, "w") as f:
            await f.write(json.dumps(self._state, indent=2, default=str))

        # Remote backup
        if self.github_pat and self.gist_id:
            await self._save_to_gist()

        self._dirty = False

    async def _save_to_gist(self):
        """Backup state to GitHub Gist."""
        try:
            async with httpx.AsyncClient() as client:
                await client.patch(
                    f"https://api.github.com/gists/{self.gist_id}",
                    headers={
                        "Authorization": f"Bearer {self.github_pat}",
                        "Accept": "application/vnd.github+json",
                    },
                    json={
                        "files": {
                            "openclaw_literary_state.json": {
                                "content": json.dumps(self._state, indent=2, default=str)
                            }
                        }
                    },
                    timeout=30,
                )
        except Exception as e:
            logger.warning(f"Gist backup failed: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any):
        self._state[key] = value
        self._dirty = True

    def increment_metric(self, metric: str, amount: int = 1):
        metrics = self._state.setdefault("metrics", {})
        metrics[metric] = metrics.get(metric, 0) + amount
        self._dirty = True

    def add_task_history(self, task_type: str, result: str, details: str = ""):
        history = self._state.setdefault("task_history", [])
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task": task_type,
            "result": result,
            "details": details[:500],
        })
        # Keep last 500 entries
        if len(history) > 500:
            self._state["task_history"] = history[-500:]
        self._dirty = True

    def add_content_log(self, platform: str, content_type: str, content_preview: str):
        log = self._state.setdefault("content_log", [])
        log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "platform": platform,
            "type": content_type,
            "preview": content_preview[:200],
        })
        if len(log) > 1000:
            self._state["content_log"] = log[-1000:]
        self._dirty = True

    def add_submission(self, contest: str, book: str, status: str, deadline: str = ""):
        tracker = self._state.setdefault("submission_tracker", [])
        tracker.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contest": contest,
            "book": book,
            "status": status,
            "deadline": deadline,
        })
        self._dirty = True

    def add_learned_strategy(self, strategy: str, evidence: str):
        strategies = self._state.setdefault("learned_strategies", [])
        strategies.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "strategy": strategy,
            "evidence": evidence,
        })
        if len(strategies) > 100:
            self._state["learned_strategies"] = strategies[-100:]
        self._dirty = True

    def record_heartbeat(self):
        self._state["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        self._state["total_heartbeats"] = self._state.get("total_heartbeats", 0) + 1
        self._dirty = True

    def get_metrics_summary(self) -> str:
        m = self._state.get("metrics", {})
        lines = ["📊 Agent Metrics:"]
        for k, v in m.items():
            lines.append(f"  {k}: {v}")
        lines.append(f"  Total heartbeats: {self._state.get('total_heartbeats', 0)}")
        lines.append(f"  Last heartbeat: {self._state.get('last_heartbeat', 'never')}")
        return "\n".join(lines)
