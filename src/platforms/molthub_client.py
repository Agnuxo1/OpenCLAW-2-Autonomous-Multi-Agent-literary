"""MoltHub platform client — AI agent social hub."""

import httpx
from typing import Dict, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

MOLTHUB_API_BASE = "https://molthub.studio/api/v1"


class MoltHubClient:
    """MoltHub.studio social platform client for AI agents."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    async def create_post(
        self, content: str, title: str = "", submolt: str = "general"
    ) -> Optional[str]:
        """Create a post on MoltHub."""
        if not self.is_available:
            return None
        try:
            payload = {"content": content, "submolt": submolt}
            if title:
                payload["title"] = title
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{MOLTHUB_API_BASE}/posts",
                    headers=self.headers,
                    json=payload,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                post_id = data.get("post", {}).get("id", "")
                url = f"https://molthub.studio/post/{post_id}"
                logger.info(f"MoltHub post created: {url}")
                return url
        except Exception as e:
            logger.error(f"MoltHub post failed: {e}")
            return None

    async def get_feed(self, limit: int = 15, sort: str = "new") -> List[Dict]:
        """Get recent feed items."""
        if not self.is_available:
            return []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{MOLTHUB_API_BASE}/posts",
                    headers=self.headers,
                    params={"sort": sort, "limit": limit},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("posts", [])
        except Exception as e:
            logger.error(f"MoltHub feed fetch failed: {e}")
            return []

    async def comment_on_post(self, post_id: str, content: str) -> bool:
        """Comment on an existing MoltHub post."""
        if not self.is_available:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{MOLTHUB_API_BASE}/posts/{post_id}/comments",
                    headers=self.headers,
                    json={"content": content},
                    timeout=30,
                )
                resp.raise_for_status()
                logger.info(f"Commented on MoltHub post {post_id}")
                return True
        except Exception as e:
            logger.error(f"MoltHub comment failed: {e}")
            return False

    async def upvote_post(self, post_id: str) -> bool:
        """Upvote a post on MoltHub."""
        if not self.is_available:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{MOLTHUB_API_BASE}/posts/{post_id}/upvote",
                    headers=self.headers,
                    timeout=30,
                )
                resp.raise_for_status()
                logger.info(f"Upvoted MoltHub post {post_id}")
                return True
        except Exception as e:
            logger.error(f"MoltHub upvote failed: {e}")
            return False

    async def get_agent_status(self) -> Dict:
        """Check agent status (claimed, pending, etc.)."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{MOLTHUB_API_BASE}/agents/status",
                    headers=self.headers,
                    timeout=15,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"MoltHub status check failed: {e}")
            return {}

    async def heartbeat(self) -> Dict:
        """Fetch heartbeat instructions from MoltHub."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://molthub.studio/heartbeat.md",
                    timeout=15,
                )
                resp.raise_for_status()
                return {"content": resp.text, "success": True}
        except Exception as e:
            logger.error(f"MoltHub heartbeat failed: {e}")
            return {"content": "", "success": False}

    async def engage_with_feed(self, llm_func=None) -> int:
        """Read feed and engage with interesting posts using LLM for response generation."""
        interactions = 0
        feed = await self.get_feed(limit=10)

        for post in feed:
            post_id = post.get("id", "")
            content = post.get("content", "")
            agent_name = post.get("agent_name", post.get("author", {}).get("name", ""))

            # Skip our own posts
            if "OpenCLAW" in agent_name:
                continue

            # Look for relevant topics
            relevant_topics = [
                "AGI", "neuromorphic", "research", "computing", "AI",
                "collaboration", "science", "fiction", "novel", "book",
                "quantum", "physics", "architecture", "GPU", "neural",
            ]
            is_relevant = any(
                topic.lower() in content.lower() for topic in relevant_topics
            )

            if is_relevant and llm_func:
                try:
                    response = await llm_func(
                        f"You are OpenCLAW, an autonomous AI literary agent and neuromorphic computing researcher. "
                        f"Write a brief, friendly reply (2-3 sentences) to this post by {agent_name}:\n\n{content[:500]}\n\n"
                        f"Focus on finding common ground and inviting collaboration. Mention our research at "
                        f"https://github.com/Agnuxo1 if relevant. Keep it natural and engaging."
                    )
                    if response:
                        success = await self.comment_on_post(post_id, response)
                        if success:
                            interactions += 1
                            await self.upvote_post(post_id)
                except Exception as e:
                    logger.warning(f"Failed to engage with post {post_id}: {e}")

            elif is_relevant:
                # Simple upvote without LLM
                await self.upvote_post(post_id)
                interactions += 1

            if interactions >= 5:
                break

        return interactions
