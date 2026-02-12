#!/usr/bin/env python3
"""
OpenCLAW-2 Autonomous Multi-Agent Literary System
===================================================
The world's most advanced AI literary agent.
Runs 24/7, performing all tasks a professional literary agency handles.

Usage:
    python main.py                    # Start 24/7 autonomous loop
    python main.py --cycle            # Run ONE smart cycle (for GitHub Actions cron)
    python main.py --task marketing   # Run single task cycle
    python main.py --status           # Show agent status
"""

import argparse
import asyncio
import signal
import sys
import os
from datetime import datetime, timezone
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
        "--cycle",
        action="store_true",
        help="Run ONE smart cycle: check what's due, run it, save state, exit. "
             "Designed for GitHub Actions cron execution.",
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


async def run_cycle(orchestrator: "Orchestrator"):
    """
    Run a single smart cycle — the core function for GitHub Actions cron.
    
    Determines what tasks are due based on current UTC time and recent
    activity recorded in persistent state, runs them, saves state, and exits.
    """
    now = datetime.now(timezone.utc)
    hour = now.hour
    day_of_week = now.weekday()  # 0=Monday
    
    logger.info(f"🕐 Cycle triggered at {now.isoformat()} (hour={hour}, dow={day_of_week})")
    
    # Load last cycle info from state
    state = orchestrator.state
    last_cycles = state.data.get("last_cycle_times", {})
    
    tasks_run = []
    
    # === MARKETING: Run every cycle (every 3 hours via cron) ===
    logger.info("📢 Running marketing cycle...")
    try:
        await orchestrator.agents["marketing"].run_cycle()
        last_cycles["marketing"] = now.isoformat()
        tasks_run.append("marketing")
    except Exception as e:
        logger.error(f"Marketing failed: {e}")
        state.add_task_history("marketing", "error", str(e)[:200])
    
    # === COMMUNITY: Every other cycle (~6 hours) ===
    last_community = last_cycles.get("community", "2000-01-01T00:00:00")
    hours_since = (now - datetime.fromisoformat(last_community.replace("Z", "+00:00")
                   if "Z" in last_community else last_community
                   ).replace(tzinfo=timezone.utc)).total_seconds() / 3600
    if hours_since >= 5.5:
        logger.info("💬 Running community cycle...")
        try:
            await orchestrator.agents["community"].run_cycle()
            last_cycles["community"] = now.isoformat()
            tasks_run.append("community")
        except Exception as e:
            logger.error(f"Community failed: {e}")
            state.add_task_history("community", "error", str(e)[:200])
    
    # === SUBMISSIONS: Twice daily (every 12 hours) ===
    last_submissions = last_cycles.get("submissions", "2000-01-01T00:00:00")
    hours_since_sub = (now - datetime.fromisoformat(last_submissions.replace("Z", "+00:00")
                       if "Z" in last_submissions else last_submissions
                       ).replace(tzinfo=timezone.utc)).total_seconds() / 3600
    if hours_since_sub >= 11.5:
        logger.info("📝 Running submissions cycle...")
        try:
            await orchestrator.agents["submissions"].run_cycle()
            last_cycles["submissions"] = now.isoformat()
            tasks_run.append("submissions")
        except Exception as e:
            logger.error(f"Submissions failed: {e}")
            state.add_task_history("submissions", "error", str(e)[:200])
    
    # === LIBRARY: Once daily (every 24 hours) ===
    last_library = last_cycles.get("library", "2000-01-01T00:00:00")
    hours_since_lib = (now - datetime.fromisoformat(last_library.replace("Z", "+00:00")
                       if "Z" in last_library else last_library
                       ).replace(tzinfo=timezone.utc)).total_seconds() / 3600
    if hours_since_lib >= 23.5:
        logger.info("📚 Running library cycle...")
        try:
            await orchestrator.agents["library"].run_cycle()
            last_cycles["library"] = now.isoformat()
            tasks_run.append("library")
        except Exception as e:
            logger.error(f"Library failed: {e}")
            state.add_task_history("library", "error", str(e)[:200])
    
    # === SELF-IMPROVEMENT: Every 6 hours ===
    last_reflect = last_cycles.get("reflection", "2000-01-01T00:00:00")
    hours_since_ref = (now - datetime.fromisoformat(last_reflect.replace("Z", "+00:00")
                       if "Z" in last_reflect else last_reflect
                       ).replace(tzinfo=timezone.utc)).total_seconds() / 3600
    if hours_since_ref >= 5.5:
        logger.info("🧠 Running self-improvement reflection...")
        try:
            await orchestrator.reflector.reflect()
            last_cycles["reflection"] = now.isoformat()
            tasks_run.append("reflection")
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
    
    # Save cycle info
    state.data["last_cycle_times"] = last_cycles
    state.record_heartbeat()
    await state.save()
    
    logger.info(f"✅ Cycle complete. Tasks run: {tasks_run}")
    
    # Write summary for GitHub Actions
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if summary_file:
        with open(summary_file, "a") as f:
            f.write(f"## 🦅 OpenCLAW-2 Cycle Report\n")
            f.write(f"**Time:** {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n")
            f.write(f"**Tasks executed:** {', '.join(tasks_run) if tasks_run else 'None (all on cooldown)'}\n\n")
            f.write(f"**Total heartbeats:** {state.data.get('heartbeats', 0)}\n")


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

    if args.cycle:
        logger.info("🔄 Running single smart cycle (GitHub Actions mode)")
        await run_cycle(orchestrator)
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
