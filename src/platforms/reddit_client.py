"""Reddit platform client for community engagement."""

import asyncio
from typing import Dict, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RedditClient:
    """Manages Reddit posting and community engagement."""

    def __init__(self, client_id: str, client_secret: str, username: str, password: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self._reddit = None

    async def initialize(self):
        """Set up Reddit connection."""
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            logger.warning("Reddit credentials incomplete — Reddit client disabled")
            return False
        try:
            import praw
            self._reddit = await asyncio.to_thread(
                praw.Reddit,
                client_id=self.client_id,
                client_secret=self.client_secret,
                username=self.username,
                password=self.password,
                user_agent="OpenCLAW-LiteraryAgent/2.0 by /u/" + self.username,
            )
            logger.info(f"Reddit connected as /u/{self.username}")
            return True
        except Exception as e:
            logger.error(f"Reddit init failed: {e}")
            return False

    @property
    def is_available(self) -> bool:
        return self._reddit is not None

    async def post_to_subreddit(self, subreddit: str, title: str, body: str) -> Optional[str]:
        """Create a text post in a subreddit. Returns post URL or None."""
        if not self.is_available:
            return None
        try:
            sub = await asyncio.to_thread(self._reddit.subreddit, subreddit)
            submission = await asyncio.to_thread(sub.submit, title, selftext=body)
            url = f"https://reddit.com{submission.permalink}"
            logger.info(f"Posted to r/{subreddit}: {url}")
            return url
        except Exception as e:
            logger.error(f"Reddit post failed (r/{subreddit}): {e}")
            return None

    async def comment_on_post(self, post_url: str, comment: str) -> bool:
        """Add a comment to an existing post."""
        if not self.is_available:
            return False
        try:
            submission = await asyncio.to_thread(
                self._reddit.submission, url=post_url
            )
            await asyncio.to_thread(submission.reply, comment)
            logger.info(f"Commented on: {post_url}")
            return True
        except Exception as e:
            logger.error(f"Reddit comment failed: {e}")
            return False

    async def find_relevant_posts(self, subreddit: str, query: str, limit: int = 10) -> List[Dict]:
        """Search for relevant posts to engage with."""
        if not self.is_available:
            return []
        try:
            sub = await asyncio.to_thread(self._reddit.subreddit, subreddit)
            results = []
            for post in sub.search(query, limit=limit, sort="new"):
                results.append({
                    "title": post.title,
                    "url": f"https://reddit.com{post.permalink}",
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "created": post.created_utc,
                })
            return results
        except Exception as e:
            logger.error(f"Reddit search failed: {e}")
            return []

    # Target subreddits for literary engagement
    LITERARY_SUBREDDITS = [
        "books", "scifi", "printSF", "sciencefiction", "fantasy",
        "booksuggestions", "suggestmeabook", "selfpublish",
        "writing", "writerscircle", "dystopianbooks",
        "thrillerbooks", "horrorlit", "cyberpunk",
    ]
