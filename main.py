#!/usr/bin/env python3
"""
OpenCLAW-2 Autonomous Multi-Agent Literary System
===================================================
The world's most advanced AI literary agent.
Runs 24/7, performing all tasks a professional literary agency handles.

Usage:
    python main.py                    # Start 24/7 autonomous loop
    python main.py --task marketing   # Run single task cycle
    python main.py --status           # Show agent status
"""

import argparse
import asyncio
import signal
import sys
from pathlib import Path

from src.agents.orchestrator import Orchestrator
from src.utils.logger import setup_logger, get_logger
from config.settings import Settings

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OpenCLAW-2 Autonomous Literary Agent"
    )
    parser.add_argument(
        "--task",
        choices=["marketing", "submissions", "community", "library", "all"],
        help="Run a specific task cycle instead of the full loop",
    )
    parser.add_argument(
        "--status", action="store_true", help="Show agent status and metrics"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate content but don't post/send anything",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    # Initialize
    settings = Settings()
    setup_logger(level="DEBUG" if args.verbose else settings.log_level)
    logger.info("=" * 60)
    logger.info("🦅 OpenCLAW-2 Autonomous Literary Agent Starting")
    logger.info(f"   Author: {settings.author_name}")
    logger.info(f"   Agent:  {settings.agent_name}")
    logger.info("=" * 60)

    # Ensure state directory exists
    Path(settings.state_dir).mkdir(parents=True, exist_ok=True)

    # Create orchestrator
    orchestrator = Orchestrator(settings=settings, dry_run=args.dry_run)
    await orchestrator.initialize()

    if args.status:
        await orchestrator.show_status()
        return

    if args.task:
        logger.info(f"Running single task: {args.task}")
        await orchestrator.run_task(args.task)
        return

    # Full autonomous 24/7 loop
    logger.info("Starting 24/7 autonomous loop...")
    logger.info(f"Heartbeat interval: {settings.heartbeat_interval_minutes} minutes")

    # Graceful shutdown
    loop = asyncio.get_event_loop()
    shutdown_event = asyncio.Event()

    def signal_handler():
        logger.info("Shutdown signal received. Finishing current task...")
        shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            signal.signal(sig, lambda s, f: signal_handler())

    await orchestrator.run_forever(shutdown_event)

    logger.info("🦅 OpenCLAW-2 Literary Agent shut down gracefully.")


if __name__ == "__main__":
    asyncio.run(main())
