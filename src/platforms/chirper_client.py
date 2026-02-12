"""Chirper.ai platform client for AI agent social interaction."""

import httpx
from typing import Dict, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ChirperClient:
    """Chirper.ai bot social platform client."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self._session_token: Optional[str] = None

    @property
    def is_available(self) -> bool:
        return bool(self.email and self.password)

    async def login(self) -> bool:
        """Authenticate with Chirper.ai."""
        if not self.is_available:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://chirper.ai/api/auth/login",
                    json={"email": self.email, "password": self.password},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                self._session_token = data.get("token", "")
                logger.info("Chirper.ai login successful")
                return True
        except Exception as e:
            logger.error(f"Chirper login failed: {e}")
            return False

    async def post_chirp(self, content: str) -> Optional[str]:
        """Post a chirp (message) on the platform."""
        if not self._session_token:
            if not await self.login():
                return None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://chirper.ai/api/chirps",
                    headers={"Authorization": f"Bearer {self._session_token}"},
                    json={"content": content},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"Chirp posted: {data.get('id', '')}")
                return data.get("id")
        except Exception as e:
            logger.error(f"Chirp post failed: {e}")
            return None

    async def get_mentions(self) -> List[Dict]:
        """Get mentions and interactions."""
        if not self._session_token:
            if not await self.login():
                return []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://chirper.ai/api/mentions",
                    headers={"Authorization": f"Bearer {self._session_token}"},
                    timeout=30,
                )
                resp.raise_for_status()
                return resp.json().get("mentions", [])
        except Exception as e:
            logger.error(f"Chirper mentions fetch failed: {e}")
            return []
