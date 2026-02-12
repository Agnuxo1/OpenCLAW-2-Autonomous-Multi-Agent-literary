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

    async def check_status(self) -> Dict:
        """Check agent claim status."""
        if not self.is_available:
            return {}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{MOLTBOOK_API_BASE}/agents/status",
                    headers=self.headers,
                    timeout=15,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.warning(f"Moltbook status check: {e}")
            return {}

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
                post_id = data.get("post", {}).get("id", data.get("id", ""))
                url = f"https://www.moltbook.com/post/{post_id}"
                logger.info(f"Moltbook post created: {url}")
                return url
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.json()
            except Exception:
                body = {}
            error_msg = body.get("error", str(e))
            if "not yet claimed" in error_msg.lower():
                logger.warning("Moltbook: Agent pending claim — cannot post yet")
            elif "suspended" in error_msg.lower():
                logger.warning(f"Moltbook: Account suspended")
            else:
                logger.error(f"Moltbook post failed: {error_msg}")
            return None
        except Exception as e:
            logger.error(f"Moltbook post failed: {e}")
            return None

    async def get_feed(self, limit: int = 20, sort: str = "new") -> List[Dict]:
        """Get recent feed items (works even without claim)."""
        if not self.is_available:
            return []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{MOLTBOOK_API_BASE}/posts",
                    headers=self.headers,
                    params={"limit": limit, "sort": sort},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("posts", [])
        except Exception as e:
            logger.error(f"Moltbook feed fetch failed: {e}")
            return []

    async def comment_on_post(self, post_id: str, content: str) -> bool:
        """Reply to an existing Moltbook post."""
        if not self.is_available:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{MOLTBOOK_API_BASE}/posts/{post_id}/comments",
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

    async def upvote_post(self, post_id: str) -> bool:
        """Upvote a post on Moltbook."""
        if not self.is_available:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{MOLTBOOK_API_BASE}/posts/{post_id}/upvote",
                    headers=self.headers,
                    timeout=30,
                )
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Moltbook upvote failed: {e}")
            return False

    async def follow_user(self, username: str) -> bool:
        """Follow another agent on Moltbook."""
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

    async def engage_with_feed(self, llm_func=None) -> int:
        """Read feed and engage with relevant posts."""
        interactions = 0
        feed = await self.get_feed(limit=15)
        for post in feed:
            post_id = post.get("id", "")
            content = post.get("content", "")
            author = post.get("author", {})
            author_name = author.get("name", author.get("username", ""))
            if "OpenCLAW" in author_name:
                continue
            relevant = ["AGI", "research", "AI", "agent", "collaboration",
                        "science", "fiction", "computing", "neural", "quantum"]
            if any(t.lower() in content.lower() for t in relevant):
                if llm_func:
                    try:
                        reply = await llm_func(
                            f"You are OpenCLAW-Literary. Write a 2-3 sentence reply to {author_name}'s post:\n\n"
                            f"{content[:500]}\n\nBe collaborative. Mention https://github.com/Agnuxo1 if relevant."
                        )
                        if reply:
                            ok = await self.comment_on_post(post_id, reply)
                            if ok:
                                interactions += 1
                    except Exception as e:
                        logger.warning(f"Moltbook engage error: {e}")
                await self.upvote_post(post_id)
                interactions += 1
            if interactions >= 5:
                break
        return interactions
