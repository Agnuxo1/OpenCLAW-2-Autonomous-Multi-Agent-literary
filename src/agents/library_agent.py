"""
Library Outreach Agent — Requests book additions to libraries.
"""

import random
from typing import Dict, List
from config.author_profile import ENGLISH_NOVELS, Book
from src.marketing.content_generator import ContentGenerator
from src.utils.web_scraper import WebScraper
from src.memory.persistent_state import PersistentState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Known library systems that accept online acquisition requests
LIBRARY_TARGETS = [
    {"name": "New York Public Library", "type": "public", "url": "https://www.nypl.org/"},
    {"name": "Los Angeles Public Library", "type": "public", "url": "https://www.lapl.org/"},
    {"name": "Chicago Public Library", "type": "public", "url": "https://www.chipublib.org/"},
    {"name": "British Library", "type": "national", "url": "https://www.bl.uk/"},
    {"name": "Library of Congress", "type": "national", "url": "https://www.loc.gov/"},
    {"name": "Internet Archive Open Library", "type": "digital", "url": "https://openlibrary.org/"},
    {"name": "Project Gutenberg", "type": "digital", "url": "https://www.gutenberg.org/"},
]


class LibraryAgent:
    """Autonomous agent for library outreach and catalog presence."""

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
        """Execute one library outreach cycle."""
        logger.info("📚 Library Agent: Starting cycle")
        results = {"requests_prepared": 0, "libraries_contacted": 0, "errors": []}

        # Select a book for this cycle
        book = random.choice(ENGLISH_NOVELS)
        logger.info(f"  Book for outreach: '{book.title}'")

        # Generate acquisition request letters
        for library in random.sample(LIBRARY_TARGETS, min(2, len(LIBRARY_TARGETS))):
            try:
                letter = await self.content_gen.generate_library_request(
                    book, library["name"]
                )

                if self.dry_run:
                    logger.info(f"  [DRY RUN] Library request for {library['name']}")
                else:
                    self.state.add_content_log(
                        "library", "request", f"{library['name']}: {book.title}"
                    )
                    results["requests_prepared"] += 1
                    self.state.increment_metric("library_requests")
            except Exception as e:
                results["errors"].append(f"{library['name']}: {e}")
                logger.error(f"Library request error ({library['name']}): {e}")

        # Search for additional library opportunities
        try:
            new_libraries = await self.scraper.find_libraries_for_outreach()
            logger.info(f"  Found {len(new_libraries)} additional library opportunities")
        except Exception as e:
            logger.warning(f"Library search error: {e}")

        self.state.add_task_history(
            "library",
            f"Prepared {results['requests_prepared']} library requests for '{book.title}'",
        )
        logger.info(f"📚 Library cycle complete: {results['requests_prepared']} requests")
        return results
