"""
Submissions Agent — Discovers contests, generates query letters, tracks submissions.
"""

import random
from typing import Dict, List
from config.author_profile import ENGLISH_NOVELS, Book
from src.marketing.content_generator import ContentGenerator
from src.utils.web_scraper import WebScraper
from src.memory.persistent_state import PersistentState
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SubmissionsAgent:
    """Autonomous agent for literary contest discovery and submission."""

    def __init__(
        self,
        content_gen: ContentGenerator,
        web_scraper: WebScraper,
        email_client,
        state: PersistentState,
        dry_run: bool = False,
    ):
        self.content_gen = content_gen
        self.scraper = web_scraper
        self.email = email_client
        self.state = state
        self.dry_run = dry_run

    async def run_cycle(self) -> Dict:
        """Execute one submissions cycle: discover → evaluate → submit."""
        logger.info("📝 Submissions Agent: Starting cycle")
        results = {"contests_found": 0, "submissions_prepared": 0, "errors": []}

        # Step 1: Discover contests
        contests = await self._discover_contests()
        results["contests_found"] = len(contests)
        logger.info(f"  Found {len(contests)} potential contests/opportunities")

        # Step 2: For each contest, prepare a submission
        for contest in contests[:3]:  # Max 3 per cycle
            try:
                book = self._match_book_to_contest(contest)
                if not book:
                    continue

                query_letter = await self.content_gen.generate_query_letter(
                    book, target_description=contest.get("description", "")
                )

                if self.dry_run:
                    logger.info(
                        f"  [DRY RUN] Prepared query for '{book.title}' → {contest['title'][:60]}"
                    )
                else:
                    self.state.add_submission(
                        contest=contest["title"],
                        book=book.title,
                        status="prepared",
                        deadline=contest.get("deadline", "unknown"),
                    )

                results["submissions_prepared"] += 1
                self.state.increment_metric("submissions_made")
            except Exception as e:
                results["errors"].append(str(e))
                logger.error(f"Submission prep error: {e}")

        self.state.add_task_history(
            "submissions",
            f"Found {results['contests_found']} contests, prepared {results['submissions_prepared']} submissions",
        )
        logger.info(f"📝 Submissions cycle complete: {results['submissions_prepared']} prepared")
        return results

    async def _discover_contests(self) -> List[Dict]:
        """Search for open literary contests and awards."""
        raw_results = await self.scraper.find_literary_contests()

        # Deduplicate and filter
        seen_urls = set()
        contests = []
        for r in raw_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                contests.append(r)
        return contests

    def _match_book_to_contest(self, contest: Dict) -> Book:
        """Match the best book to a contest based on genre."""
        desc = (contest.get("title", "") + " " + contest.get("description", "")).lower()

        genre_keywords = {
            "sci-fi": ["science fiction", "sci-fi", "speculative", "futuristic"],
            "thriller": ["thriller", "mystery", "suspense", "crime"],
            "horror": ["horror", "gothic", "dark fiction", "supernatural"],
            "general": ["literary", "fiction", "novel", "book"],
        }

        for book in ENGLISH_NOVELS:
            book_genres = book.genre.lower()
            for genre_key, keywords in genre_keywords.items():
                if any(kw in desc for kw in keywords) and any(
                    kw in book_genres for kw in keywords
                ):
                    return book

        # Default to a random English novel
        return random.choice(ENGLISH_NOVELS)
