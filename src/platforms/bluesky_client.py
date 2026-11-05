# Project: OpenCLAW-2 Autonomous Multi-Agent Literary System
# Project attribution: Francisco Angulo de Lafuente
# Copyright 2024-2026 Francisco Angulo de Lafuente / OpenCLAW Project
# ORCID: https://orcid.org/0009-0001-1634-7063
# Attribution recorded: 2026-11-05
# SPDX-License-Identifier: Apache-2.0

"""Bluesky (AT Protocol) client for social media posting."""

from typing import Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BlueskyClient:
    """Bluesky social network client using atproto."""

    def __init__(self, handle: str, app_password: str):
        self.handle = handle
        self.app_password = app_password
        self._client = None

    @property
    def is_available(self) -> bool:
        return bool(self.handle and self.app_password)

    async def initialize(self) -> bool:
        """Login to Bluesky."""
        if not self.is_available:
            logger.warning("Bluesky credentials not configured")
            return False
        try:
            from atproto import Client
            self._client = Client()
            self._client.login(self.handle, self.app_password)
            logger.info(f"Bluesky connected as @{self.handle}")
            return True
        except Exception as e:
            logger.error(f"Bluesky login failed: {e}")
            return False

    async def post(self, text: str) -> Optional[str]:
        """Create a Bluesky post."""
        if not self._client:
            if not await self.initialize():
                return None
        try:
            resp = self._client.send_post(text=text[:300])
            uri = getattr(resp, "uri", "posted")
            logger.info(f"Bluesky post created: {uri}")
            return str(uri)
        except Exception as e:
            logger.error(f"Bluesky post failed: {e}")
            return None
