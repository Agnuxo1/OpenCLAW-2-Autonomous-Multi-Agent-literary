"""
Orchestrator — The central brain of the OpenCLAW Literary Agent.
Manages the 24/7 heartbeat loop, task scheduling, and agent coordination.
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import Dict, Optional

from config.settings import Settings
from src.utils.llm_pool import LLMPool
from src.utils.web_scraper import WebScraper
from src.utils.logger import get_logger
from src.memory.persistent_state import PersistentState
from src.marketing.content_generator import ContentGenerator
from src.agents.marketing_agent import MarketingAgent
from src.agents.submissions_agent import SubmissionsAgent
from src.agents.community_agent import CommunityAgent
from src.agents.library_agent import LibraryAgent
from src.self_improvement.strategy_reflector import StrategyReflector
from src.platforms.reddit_client import RedditClient
from src.platforms.moltbook_client import MoltbookClient
from src.platforms.chirper_client import ChirperClient
from src.platforms.bluesky_client import BlueskyClient
from src.platforms.email_client import EmailClient
from src.platforms.blog_manager import BlogManager

logger = get_logger(__name__)


class Orchestrator:
    """
    Central orchestrator for the autonomous literary agent.
    Coordinates all sub-agents and manages the 24/7 loop.
    """

    def __init__(self, settings: Settings, dry_run: bool = False):
        self.settings = settings
        self.dry_run = dry_run
        self.llm_pool: Optional[LLMPool] = None
        self.state: Optional[PersistentState] = None
        self.content_gen: Optional[ContentGenerator] = None
        self.reflector: Optional[StrategyReflector] = None
        self.platforms: Dict = {}
        self.agents: Dict = {}
        self._heartbeat_count = 0

    async def initialize(self):
        """Set up all components."""
        logger.info("Initializing Orchestrator...")

        # Core systems
        self.llm_pool = LLMPool(self.settings)
        self.state = PersistentState(
            state_dir=self.settings.state_dir,
            github_pat=self.settings.github_pat,
            gist_id=self.settings.github_gist_id,
        )
        await self.state.load()

        self.web_scraper = WebScraper(brave_api_key=self.settings.brave_api_key)
        self.content_gen = ContentGenerator(self.llm_pool)
        self.reflector = StrategyReflector(self.llm_pool, self.state)

        # Initialize platforms
        await self._init_platforms()

        # Initialize agents
        self.agents["marketing"] = MarketingAgent(
            self.content_gen, self.platforms, self.state, self.dry_run
        )
        self.agents["submissions"] = SubmissionsAgent(
            self.content_gen, self.web_scraper,
            self.platforms.get("email"), self.state, self.dry_run
        )
        self.agents["community"] = CommunityAgent(
            self.content_gen, self.platforms, self.state, self.dry_run
        )
        self.agents["library"] = LibraryAgent(
            self.content_gen, self.web_scraper,
            self.platforms.get("email"), self.state, self.dry_run
        )

        logger.info(f"Orchestrator initialized with {len(self.agents)} agents")
        logger.info(f"Platforms available: {[k for k, v in self.platforms.items() if v and (hasattr(v, 'is_available') and v.is_available or not hasattr(v, 'is_available'))]}")

    async def _init_platforms(self):
        """Initialize all platform clients."""
        # Reddit
        reddit = RedditClient(
            self.settings.reddit_client_id,
            self.settings.reddit_client_secret,
            self.settings.reddit_username,
            self.settings.reddit_password,
        )
        if await reddit.initialize():
            self.platforms["reddit"] = reddit

        # Moltbook
        moltbook = MoltbookClient(self.settings.moltbook_api_key)
        if moltbook.is_available:
            self.platforms["moltbook"] = moltbook

        # Chirper
        chirper = ChirperClient(self.settings.chirper_email, self.settings.chirper_password)
        if chirper.is_available:
            self.platforms["chirper"] = chirper

        # Bluesky
        bluesky = BlueskyClient(self.settings.bluesky_handle, self.settings.bluesky_app_password)
        if await bluesky.initialize():
            self.platforms["bluesky"] = bluesky

        # Email
        email = EmailClient(
            self.settings.smtp_host,
            self.settings.smtp_port,
            self.settings.smtp_user,
            self.settings.smtp_password,
            self.settings.email_from_name,
        )
        if email.is_available:
            self.platforms["email"] = email

        # Blog
        self.platforms["blog"] = BlogManager(f"{self.settings.state_dir}/blog")

    async def run_task(self, task_name: str):
        """Run a single task cycle."""
        if task_name == "all":
            for name, agent in self.agents.items():
                try:
                    await agent.run_cycle()
                except Exception as e:
                    logger.error(f"Agent '{name}' cycle failed: {e}")
        elif task_name in self.agents:
            await self.agents[task_name].run_cycle()
        else:
            logger.error(f"Unknown task: {task_name}")

        await self.state.save()

    async def run_forever(self, shutdown_event: asyncio.Event):
        """
        Main 24/7 autonomous loop.
        
        Schedule:
        - Every 30 min: heartbeat + one task cycle
        - Every 2 hours: full marketing cycle
        - Every 6 hours: community engagement
        - Every 12 hours: submissions check
        - Every 24 hours: library outreach + daily review
        """
        logger.info("🦅 Entering autonomous 24/7 loop")
        interval = self.settings.heartbeat_interval_minutes * 60

        while not shutdown_event.is_set():
            try:
                self._heartbeat_count += 1
                now = datetime.now(timezone.utc)
                hour = now.hour

                logger.info(f"💓 Heartbeat #{self._heartbeat_count} at {now.isoformat()}")
                self.state.record_heartbeat()

                # Determine which tasks to run based on schedule
                tasks_to_run = self._get_scheduled_tasks(hour)

                for task_name in tasks_to_run:
                    agent = self.agents.get(task_name)
                    if agent:
                        try:
                            logger.info(f"  Running: {task_name}")
                            await agent.run_cycle()
                            self.state.increment_metric("total_llm_calls")
                        except Exception as e:
                            logger.error(f"  Agent '{task_name}' failed: {e}")
                            self.state.add_task_history(task_name, "error", str(e)[:200])

                # Self-reflection every 12 heartbeats (~6 hours)
                if self._heartbeat_count % 12 == 0:
                    try:
                        await self.reflector.reflect()
                    except Exception as e:
                        logger.error(f"Reflection failed: {e}")

                # Daily summary at configured hour
                if hour == self.settings.daily_review_hour and self._heartbeat_count > 1:
                    try:
                        summary = await self.reflector.generate_daily_summary()
                        logger.info(summary)
                    except Exception as e:
                        logger.error(f"Daily summary failed: {e}")

                # Save state after each heartbeat
                await self.state.save()

            except Exception as e:
                logger.error(f"Heartbeat error: {e}")

            # Wait for next heartbeat or shutdown
            try:
                await asyncio.wait_for(
                    shutdown_event.wait(), timeout=interval
                )
                break  # Shutdown requested
            except asyncio.TimeoutError:
                pass  # Normal timeout, continue loop

    def _get_scheduled_tasks(self, hour: int) -> list:
        """Determine which tasks to run based on current hour."""
        tasks = []

        # Marketing: every 2 hours (most frequent)
        if self._heartbeat_count % 4 == 1:  # ~every 2 hours
            tasks.append("marketing")

        # Community: every 6 hours
        if self._heartbeat_count % 12 == 3:
            tasks.append("community")

        # Submissions: every 12 hours
        if self._heartbeat_count % 24 == 5:
            tasks.append("submissions")

        # Library: once daily at a quiet hour
        if hour == 10 and self._heartbeat_count % 48 == 7:
            tasks.append("library")

        # If nothing scheduled, do a small marketing/community task
        if not tasks:
            tasks.append(random.choice(["marketing", "community"]))

        return tasks

    async def show_status(self):
        """Display current agent status."""
        print("\n" + "=" * 60)
        print("🦅 OpenCLAW-2 Literary Agent — Status Report")
        print("=" * 60)
        print(self.state.get_metrics_summary())
        print(f"\nHeartbeats this session: {self._heartbeat_count}")
        print(f"Dry run mode: {self.dry_run}")
        print(f"\nPlatforms:")
        for name, platform in self.platforms.items():
            available = getattr(platform, "is_available", True)
            status = "✅" if available else "❌"
            print(f"  {status} {name}")
        print(f"\nLLM Pool:")
        pool_status = self.llm_pool.get_status()
        for p in pool_status["providers"]:
            available_keys = sum(1 for k in p["keys"] if k["available"])
            print(f"  {p['type']}: {available_keys}/{len(p['keys'])} keys available ({p['model']})")
        print(f"  Total LLM calls: {pool_status['total_calls']}")
        print("=" * 60)
