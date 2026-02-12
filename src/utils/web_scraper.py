"""Web scraping and search utilities for research tasks."""

import asyncio
from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WebScraper:
    """Async web scraper for literary research."""

    def __init__(self, brave_api_key: str = ""):
        self.brave_api_key = brave_api_key
        self.headers = {
            "User-Agent": "OpenCLAW-LiteraryAgent/2.0 (Research Bot; +https://openclaw.ai/)"
        }

    async def search_brave(self, query: str, count: int = 10) -> List[Dict]:
        """Search using Brave Search API."""
        if not self.brave_api_key:
            logger.warning("Brave API key not set, falling back to direct scraping")
            return []

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": count},
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": self.brave_api_key,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            for r in data.get("web", {}).get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "description": r.get("description", ""),
                })
            return results

    async def fetch_page(self, url: str) -> str:
        """Fetch and extract text from a webpage."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            # Remove scripts, styles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)[:5000]

    async def find_literary_contests(self) -> List[Dict]:
        """Search for current literary contests and submissions."""
        queries = [
            "science fiction writing contest 2026 submissions open",
            "sci-fi novel award submissions deadline",
            "speculative fiction contest open submissions",
            "thriller novel writing competition 2026",
            "international book awards submissions",
        ]
        all_results = []
        for q in queries:
            try:
                results = await self.search_brave(q, count=5)
                all_results.extend(results)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.warning(f"Search failed for '{q}': {e}")
        return all_results

    async def find_libraries_for_outreach(self) -> List[Dict]:
        """Find libraries that accept acquisition requests."""
        queries = [
            "public library suggest a book for purchase",
            "university library acquisition request science fiction",
            "digital library add book request",
        ]
        all_results = []
        for q in queries:
            try:
                results = await self.search_brave(q, count=5)
                all_results.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"Search failed for '{q}': {e}")
        return all_results

    async def find_book_forums(self) -> List[Dict]:
        """Find active book discussion forums and communities."""
        queries = [
            "science fiction book discussion forum active",
            "best reddit communities for sci-fi books",
            "online book clubs science fiction 2026",
        ]
        all_results = []
        for q in queries:
            try:
                results = await self.search_brave(q, count=5)
                all_results.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"Search failed for '{q}': {e}")
        return all_results
