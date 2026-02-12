"""
Meta-Cognitive Strategy Reflector
==================================
Analyzes agent performance and generates improved strategies.
Implements a reflection loop: observe → hypothesize → plan → execute.
"""

from typing import Dict, List
from src.memory.persistent_state import PersistentState
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StrategyReflector:
    """Self-improvement through performance analysis and strategy adjustment."""

    def __init__(self, llm_pool, state: PersistentState):
        self.llm = llm_pool
        self.state = state

    async def reflect(self) -> Dict:
        """Run a reflection cycle: analyze performance and suggest improvements."""
        logger.info("🧠 Strategy Reflector: Running reflection cycle")

        # Gather performance data
        metrics = self.state.get("metrics", {})
        recent_tasks = self.state.get("task_history", [])[-20:]
        learned = self.state.get("learned_strategies", [])[-10:]
        errors = self.state.get("errors", [])[-10:]

        # Generate reflection prompt
        prompt = f"""You are a meta-cognitive AI analyzing the performance of a literary marketing agent.

Current metrics:
{metrics}

Recent task results (last 20):
{self._format_tasks(recent_tasks)}

Recent errors:
{self._format_errors(errors)}

Previously learned strategies:
{self._format_strategies(learned)}

Based on this data, provide:
1. PERFORMANCE ASSESSMENT: Brief evaluation of current effectiveness
2. KEY OBSERVATIONS: What patterns do you see? What's working? What isn't?
3. NEW STRATEGIES: 2-3 specific, actionable improvements to try
4. PRIORITY: What should the agent focus on next?

Be specific and data-driven. No generic advice."""

        analysis = await self.llm.generate(
            prompt=prompt,
            system_prompt="You are a strategic advisor for an autonomous AI literary agent. Be analytical, specific, and practical.",
            max_tokens=1500,
            temperature=0.6,
        )

        # Extract and store new strategies
        self.state.add_learned_strategy(
            strategy=analysis[:500],
            evidence=f"Based on {len(recent_tasks)} recent tasks, {metrics.get('posts_created', 0)} posts created",
        )

        logger.info("🧠 Reflection complete — strategies updated")
        return {"analysis": analysis, "metrics_snapshot": metrics}

    async def generate_daily_summary(self) -> str:
        """Generate a comprehensive daily summary report."""
        metrics = self.state.get("metrics", {})
        tasks = self.state.get("task_history", [])
        content_log = self.state.get("content_log", [])

        # Count today's activities
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_tasks = [t for t in tasks if t.get("timestamp", "").startswith(today)]
        today_content = [c for c in content_log if c.get("timestamp", "").startswith(today)]

        summary = f"""
📊 OPENCLAW LITERARY AGENT — DAILY SUMMARY
{'=' * 50}
Date: {today}

📈 TODAY'S ACTIVITY:
  Tasks completed: {len(today_tasks)}
  Content pieces created: {len(today_content)}

📊 ALL-TIME METRICS:
  Total posts: {metrics.get('posts_created', 0)}
  Emails sent: {metrics.get('emails_sent', 0)}
  Submissions: {metrics.get('submissions_made', 0)}
  Forum comments: {metrics.get('forum_comments', 0)}
  Library requests: {metrics.get('library_requests', 0)}
  Total LLM calls: {metrics.get('total_llm_calls', 0)}

📝 TODAY'S CONTENT:
"""
        for c in today_content[:10]:
            summary += f"  [{c.get('platform', '?')}] {c.get('type', '?')}: {c.get('preview', '')[:60]}\n"

        if not today_content:
            summary += "  No content created today yet.\n"

        return summary

    def _format_tasks(self, tasks: List[Dict]) -> str:
        lines = []
        for t in tasks[-10:]:
            lines.append(f"  [{t.get('timestamp', '?')[:16]}] {t.get('task', '?')}: {t.get('result', '')[:80]}")
        return "\n".join(lines) if lines else "  No recent tasks."

    def _format_errors(self, errors: List) -> str:
        if not errors:
            return "  No recent errors."
        return "\n".join(f"  - {e}" for e in errors[-5:])

    def _format_strategies(self, strategies: List[Dict]) -> str:
        if not strategies:
            return "  No strategies learned yet."
        lines = []
        for s in strategies[-5:]:
            lines.append(f"  [{s.get('timestamp', '?')[:10]}] {s.get('strategy', '')[:100]}")
        return "\n".join(lines)
