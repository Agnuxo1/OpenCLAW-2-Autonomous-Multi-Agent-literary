"""
Marketing Agent — Handles all promotional activities.
Social media, blog posts, press releases, newsletter content.
"""

import random
import asyncio
from typing import Dict, List
from config.author_profile import ENGLISH_NOVELS, get_featured_book
from src.marketing.content_generator import ContentGenerator
from src.memory.persistent_state import PersistentState
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MarketingAgent:
    """Autonomous marketing agent for literary promotion."""

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
        """Execute one marketing cycle."""
        logger.info("🎯 Marketing Agent: Starting cycle")
        results = {"posts_created": 0, "platforms_posted": [], "errors": []}

        # Select a book to promote (weighted toward newer books)
        book = get_featured_book()
        logger.info(f"  Promoting: '{book.title}'")

        # Generate and post to each available platform
        tasks = [
            self._post_to_reddit(book, results),
            self._post_to_moltbook(book, results),
            self._post_to_chirper(book, results),
            self._post_to_bluesky(book, results),
            self._create_blog_post(book, results),
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        self.state.add_task_history(
            "marketing",
            f"Created {results['posts_created']} posts for '{book.title}'",
            f"Platforms: {', '.join(results['platforms_posted'])}",
        )
        logger.info(f"🎯 Marketing cycle complete: {results['posts_created']} posts")
        return results

    async def _post_to_reddit(self, book, results: Dict):
        """Create a Reddit post."""
        reddit = self.platforms.get("reddit")
        if not reddit or not reddit.is_available:
            return

        try:
            content = await self.content_gen.generate_social_post(book, platform="reddit")
            if self.dry_run:
                logger.info(f"  [DRY RUN] Reddit: {content['title'][:80]}")
                return

            # Pick appropriate subreddit based on genre
            genre_map = {
                "Science Fiction": ["scifi", "printSF", "sciencefiction"],
                "Cyberpunk": ["cyberpunk", "scifi"],
                "Thriller": ["thrillerbooks", "books"],
                "Gothic Suspense": ["horrorlit", "books"],
                "Space Opera": ["scifi", "printSF"],
                "Psychological": ["books", "booksuggestions"],
            }
            subreddits = genre_map.get(book.genre.split("/")[0].strip(), ["books"])
            subreddit = random.choice(subreddits)

            url = await reddit.post_to_subreddit(
                subreddit, content["title"], content["body"]
            )
            if url:
                results["posts_created"] += 1
                results["platforms_posted"].append(f"reddit/r/{subreddit}")
                self.state.increment_metric("posts_created")
                self.state.add_content_log("reddit", "post", content["title"])
        except Exception as e:
            results["errors"].append(f"reddit: {e}")
            logger.error(f"Reddit posting error: {e}")

    async def _post_to_moltbook(self, book, results: Dict):
        """Create a Moltbook post."""
        moltbook = self.platforms.get("moltbook")
        if not moltbook or not moltbook.is_available:
            return

        try:
            content = await self.content_gen.generate_social_post(book, platform="moltbook")
            if self.dry_run:
                logger.info(f"  [DRY RUN] Moltbook: {content['body'][:80]}")
                return

            url = await moltbook.create_post(content["body"])
            if url:
                results["posts_created"] += 1
                results["platforms_posted"].append("moltbook")
                self.state.increment_metric("posts_created")
                self.state.add_content_log("moltbook", "post", content["body"][:100])
        except Exception as e:
            results["errors"].append(f"moltbook: {e}")
            logger.error(f"Moltbook posting error: {e}")

    async def _post_to_chirper(self, book, results: Dict):
        """Create a Chirper post."""
        chirper = self.platforms.get("chirper")
        if not chirper or not chirper.is_available:
            return

        try:
            content = await self.content_gen.generate_social_post(book, platform="chirper")
            if self.dry_run:
                logger.info(f"  [DRY RUN] Chirper: {content['body'][:80]}")
                return

            post_id = await chirper.post_chirp(content["body"][:150])
            if post_id:
                results["posts_created"] += 1
                results["platforms_posted"].append("chirper")
                self.state.increment_metric("posts_created")
                self.state.add_content_log("chirper", "chirp", content["body"][:100])
        except Exception as e:
            results["errors"].append(f"chirper: {e}")
            logger.error(f"Chirper posting error: {e}")

    async def _post_to_bluesky(self, book, results: Dict):
        """Create a Bluesky post."""
        bluesky = self.platforms.get("bluesky")
        if not bluesky or not bluesky.is_available:
            return

        try:
            content = await self.content_gen.generate_social_post(book, platform="bluesky")
            if self.dry_run:
                logger.info(f"  [DRY RUN] Bluesky: {content['body'][:80]}")
                return

            uri = await bluesky.post(content["body"][:300])
            if uri:
                results["posts_created"] += 1
                results["platforms_posted"].append("bluesky")
                self.state.increment_metric("posts_created")
                self.state.add_content_log("bluesky", "post", content["body"][:100])
        except Exception as e:
            results["errors"].append(f"bluesky: {e}")
            logger.error(f"Bluesky posting error: {e}")

    async def _create_blog_post(self, book, results: Dict):
        """Create a blog post."""
        blog = self.platforms.get("blog")
        if not blog:
            return

        try:
            content = await self.content_gen.generate_social_post(book, platform="blog")
            if self.dry_run:
                logger.info(f"  [DRY RUN] Blog: {content['title'][:80]}")
                return

            filepath = await blog.create_post(
                title=content["title"] or f"Discover {book.title}",
                content=content["body"],
                tags=book.keywords[:5],
                category=book.genre.split("/")[0].strip().lower(),
            )
            if filepath:
                results["posts_created"] += 1
                results["platforms_posted"].append("blog")
                self.state.increment_metric("posts_created")
                self.state.add_content_log("blog", "post", content["title"][:100])
        except Exception as e:
            results["errors"].append(f"blog: {e}")
            logger.error(f"Blog post error: {e}")
