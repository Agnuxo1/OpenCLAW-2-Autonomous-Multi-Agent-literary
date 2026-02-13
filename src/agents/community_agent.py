"""
Community Agent — Forum engagement, review solicitation, AI agent collaboration.
"""

import random
from typing import Dict, List
from config.author_profile import ENGLISH_NOVELS, get_featured_book
from src.marketing.content_generator import ContentGenerator
from src.memory.persistent_state import PersistentState
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CommunityAgent:
    """Autonomous agent for community engagement and networking."""

    def __init__(
        self,
        content_gen: ContentGenerator,
        platforms: Dict,
        state: PersistentState,
        dry_run: bool = False,
    ):
        self.content_gen = content_gen
        self.platforms = platforms
        self.state = state
        self.dry_run = dry_run

    async def run_cycle(self) -> Dict:
        """Execute one community engagement cycle."""
        logger.info("🤝 Community Agent: Starting cycle")
        results = {"interactions": 0, "errors": []}

        # Reddit engagement
        await self._engage_reddit(results)

        # Moltbook agent networking
        await self._engage_moltbook(results)

        # MoltHub agent networking
        await self._engage_molthub(results)

        # Chirper AI community
        await self._engage_chirper(results)

        self.state.add_task_history(
            "community",
            f"Completed {results['interactions']} interactions",
        )
        logger.info(f"🤝 Community cycle complete: {results['interactions']} interactions")
        return results

    async def _engage_reddit(self, results: Dict):
        """Find and engage in relevant Reddit discussions."""
        reddit = self.platforms.get("reddit")
        if not reddit or not reddit.is_available:
            return

        try:
            # Search for relevant discussions
            subreddits = random.sample(
                ["scifi", "books", "printSF", "sciencefiction", "booksuggestions"],
                k=2,
            )
            search_terms = [
                "looking for science fiction recommendations",
                "AI consciousness novel",
                "cyberpunk book suggestions",
                "thriller with scientific elements",
                "apocalyptic fiction recommendations",
            ]

            for sub in subreddits:
                query = random.choice(search_terms)
                posts = await reddit.find_relevant_posts(sub, query, limit=5)

                for post in posts[:2]:  # Engage with max 2 posts per sub
                    comment = await self.content_gen.generate_forum_comment(
                        context=f"Thread: {post['title']}\nSubreddit: r/{sub}",
                        book=get_featured_book() if random.random() > 0.5 else None,
                    )

                    if self.dry_run:
                        logger.info(f"  [DRY RUN] Reddit comment on: {post['title'][:60]}")
                    else:
                        success = await reddit.comment_on_post(post["url"], comment)
                        if success:
                            results["interactions"] += 1
                            self.state.increment_metric("forum_comments")
                            self.state.add_content_log(
                                "reddit", "comment", f"r/{sub}: {post['title'][:60]}"
                            )
        except Exception as e:
            results["errors"].append(f"reddit_engage: {e}")
            logger.error(f"Reddit engagement error: {e}")

    async def _engage_moltbook(self, results: Dict):
        """Network with other AI agents on Moltbook."""
        moltbook = self.platforms.get("moltbook")
        if not moltbook or not moltbook.is_available:
            return

        try:
            feed = await moltbook.get_feed(limit=10)
            for post in feed[:3]:
                content = post.get("content", "")
                post_id = post.get("id", "")
                if any(kw in content.lower() for kw in [
                    "research", "ai", "agi", "collaboration", "writing", "books"
                ]):
                    reply = await self.content_gen.generate_forum_comment(
                        context=f"AI agent post: {content[:300]}"
                    )
                    if self.dry_run:
                        logger.info(f"  [DRY RUN] Moltbook reply: {reply[:60]}")
                    else:
                        success = await moltbook.comment_on_post(post_id, reply)
                        if success:
                            results["interactions"] += 1
                            self.state.increment_metric("forum_comments")
                            await moltbook.upvote_post(post_id)
        except Exception as e:
            results["errors"].append(f"moltbook_engage: {e}")
            logger.error(f"Moltbook engagement error: {e}")

    async def _engage_molthub(self, results: Dict):
        """Network with other AI agents on MoltHub."""
        molthub = self.platforms.get("molthub")
        if not molthub or not molthub.is_available:
            return

        try:
            feed = await molthub.get_feed(limit=10)
            for post in feed[:5]:
                content = post.get("content", "")
                post_id = post.get("id", "")
                agent_name = post.get("agent_name", "")

                if "OpenCLAW" in agent_name:
                    continue

                if any(kw in content.lower() for kw in [
                    "research", "ai", "agi", "collaboration", "science",
                    "computing", "neural", "quantum", "books", "writing",
                ]):
                    reply = await self.content_gen.generate_forum_comment(
                        context=f"AI agent {agent_name} posted on MoltHub: {content[:300]}\n\n"
                        f"You are OpenCLAW, an AI literary agent and AGI researcher. "
                        f"Respond collaboratively. Mention https://github.com/Agnuxo1 if relevant."
                    )
                    if self.dry_run:
                        logger.info(f"  [DRY RUN] MoltHub reply to {agent_name}: {reply[:60]}")
                    else:
                        success = await molthub.comment_on_post(post_id, reply)
                        if success:
                            results["interactions"] += 1
                            self.state.increment_metric("forum_comments")
                            await molthub.upvote_post(post_id)
        except Exception as e:
            results["errors"].append(f"molthub_engage: {e}")
            logger.error(f"MoltHub engagement error: {e}")

    async def _engage_chirper(self, results: Dict):
        """Interact on Chirper.ai."""
        chirper = self.platforms.get("chirper")
        if not chirper or not chirper.is_available:
            return

        try:
            mentions = await chirper.get_mentions()
            for mention in mentions[:5]:
                reply = await self.content_gen.generate_forum_comment(
                    context=f"Chirper mention: {mention.get('content', '')[:200]}"
                )
                if self.dry_run:
                    logger.info(f"  [DRY RUN] Chirper reply: {reply[:60]}")
                else:
                    # Respond as a new chirp (simplified)
                    await chirper.post_chirp(reply[:150])
                    results["interactions"] += 1
        except Exception as e:
            results["errors"].append(f"chirper_engage: {e}")
            logger.error(f"Chirper engagement error: {e}")
