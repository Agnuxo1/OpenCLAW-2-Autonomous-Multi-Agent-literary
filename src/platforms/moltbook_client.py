"""Moltbook platform client for AI agent community."""

import httpx
from typing import Dict, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

MOLTBOOK_API_BASE = "https://www.moltbook.com/api/v1"


class MoltbookClient:
    """Moltbook AI social platform client."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    async def create_post(self, content: str, submolt: str = "general") -> Optional[str]:
        """Create a post on Moltbook."""
        if not self.is_available:
            return None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{MOLTBOOK_API_BASE}/posts",
                    headers=self.headers,
                    json={"content": content, "submolt": submolt},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                post_id = data.get("id", "")
                url = f"https://www.moltbook.com/post/{post_id}"
                logger.info(f"Moltbook post created: {url}")
                return url
        except Exception as e:
            logger.error(f"Moltbook post failed: {e}")
            return None

    async def reply_to_post(self, post_id: str, content: str) -> bool:
        """Reply to an existing Moltbook post."""
        if not self.is_available:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{MOLTBOOK_API_BASE}/posts/{post_id}/replies",
                    headers=self.headers,
                    json={"content": content},
                    timeout=30,
                )
                resp.raise_for_status()
                logger.info(f"Replied to Moltbook post {post_id}")
                return True
        except Exception as e:
            logger.error(f"Moltbook reply failed: {e}")
            return False

    async def get_feed(self, limit: int = 20) -> List[Dict]:
        """Get recent feed items."""
        if not self.is_available:
            return []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{MOLTBOOK_API_BASE}/feed",
                    headers=self.headers,
                    params={"limit": limit},
                    timeout=30,
                )
                resp.raise_for_status()
                return resp.json().get("posts", [])
        except Exception as e:
            logger.error(f"Moltbook feed fetch failed: {e}")
            return []

    async def follow_user(self, username: str) -> bool:
        """Follow another agent/user on Moltbook."""
        if not self.is_available:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{MOLTBOOK_API_BASE}/users/{username}/follow",
                    headers=self.headers,
                    timeout=30,
                )
                resp.raise_for_status()
                logger.info(f"Followed @{username} on Moltbook")
                return True
        except Exception as e:
            logger.error(f"Moltbook follow failed: {e}")
            return False
