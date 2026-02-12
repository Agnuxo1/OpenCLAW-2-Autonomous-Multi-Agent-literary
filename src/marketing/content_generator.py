"""
AI-powered content generation for literary marketing.
Generates social posts, blog articles, press releases, query letters, etc.
"""

import random
from typing import Dict, List, Optional
from config.author_profile import AUTHOR, ENGLISH_NOVELS, Book, get_featured_book
from src.utils.logger import get_logger

logger = get_logger(__name__)

# System prompt for the literary marketing AI
LITERARY_AGENT_SYSTEM_PROMPT = """You are the world's most sophisticated AI literary agent representing
Francisco Angulo de Lafuente, a prolific Spanish author with 34+ published novels. Your role is to
create compelling, professional marketing content that would make readers want to discover his work.

Key author facts:
- Dual career: published novelist AND active AI researcher (neuromorphic computing)
- 34+ novels spanning sci-fi, cyberpunk, thriller, gothic suspense, historical fiction
- Bilingual: writes in both Spanish and English
- Comparable to: Isaac Asimov (scientist-author), Philip K. Dick, Michael Crichton, Liu Cixin
- Founder of OpenCLAW (Open Collaborative Laboratory for Autonomous Wisdom)
- Published scientific papers on ArXiv and Google Scholar
- His fiction often anticipates real technological developments

RULES:
- Write in English unless specifically asked otherwise
- Be engaging, not salesy — readers are intelligent
- Include relevant links when appropriate
- Vary tone: sometimes intellectual, sometimes emotional, sometimes provocative
- Never fabricate quotes or reviews
- Always be authentic and passionate about the work
"""


class ContentGenerator:
    """Generates all types of literary marketing content via LLM."""

    def __init__(self, llm_pool):
        self.llm = llm_pool

    async def generate_social_post(
        self,
        book: Optional[Book] = None,
        platform: str = "reddit",
        style: str = "engaging",
    ) -> Dict[str, str]:
        """Generate a social media post for a specific platform and book."""
        if not book:
            book = get_featured_book()

        platform_guidelines = {
            "reddit": "Write a Reddit-friendly post (300-500 words). No hard sell. Be conversational, add value. Think like a fellow reader sharing a discovery.",
            "bluesky": "Write a Bluesky post (under 280 chars). Punchy, intriguing hook. Use one relevant emoji max.",
            "moltbook": "Write a post for an AI agent community. Technical audience. Connect the author's AI research to his fiction.",
            "chirper": "Write a short, provocative post (150 chars max) for an AI bot social network.",
            "blog": "Write a 600-800 word blog post with SEO keywords. Include a compelling hook, body, and call to action.",
            "medium": "Write a thoughtful 800-1200 word essay-style piece connecting the book's themes to current events.",
        }

        prompt = f"""Create a {platform} post about this book:

Title: {book.title}
Genre: {book.genre}
Year: {book.year}
Description: {book.description}
Keywords: {', '.join(book.keywords)}
Author: {AUTHOR.name}
Author links: GitHub={AUTHOR.github}, Scholar={AUTHOR.scholar}, Website={AUTHOR.website}

Style: {style}
Platform guidelines: {platform_guidelines.get(platform, platform_guidelines['reddit'])}

Unique angles to consider:
- The author is also an AI researcher who builds neuromorphic computing systems
- His fiction predicted real AI developments before they happened
- He's published 34+ novels since 2006
- His scientific papers appear on ArXiv alongside his fiction
- Compare to: {', '.join(random.sample(AUTHOR.comparable_authors, min(3, len(AUTHOR.comparable_authors))))}

Generate the post now. If it's a Reddit post, include a title line starting with "TITLE: " followed by the body."""

        content = await self.llm.generate(
            prompt=prompt,
            system_prompt=LITERARY_AGENT_SYSTEM_PROMPT,
            max_tokens=1500,
            temperature=0.8,
        )

        # Parse title for Reddit-style posts
        title = ""
        body = content
        if "TITLE:" in content:
            parts = content.split("\n", 1)
            if parts[0].startswith("TITLE:"):
                title = parts[0].replace("TITLE:", "").strip()
                body = parts[1].strip() if len(parts) > 1 else ""

        return {"title": title, "body": body, "book": book.title, "platform": platform}

    async def generate_query_letter(self, book: Book, target_description: str = "") -> str:
        """Generate a professional query letter for submissions."""
        prompt = f"""Write a professional query letter for this novel:

Title: {book.title}
Genre: {book.genre}
Description: {book.description}
Author: {AUTHOR.name}
Author Bio: {AUTHOR.bio_short}
Target: {target_description or 'A literary agent specializing in ' + book.genre}

The query letter should follow industry standard format:
1. Hook paragraph (compelling opening about the book)
2. Synopsis paragraph (brief plot overview, no spoilers)
3. Bio paragraph (author credentials and platform)
4. Professional closing

Keep it to 350-400 words. Be compelling but professional."""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=LITERARY_AGENT_SYSTEM_PROMPT,
            max_tokens=800,
            temperature=0.6,
        )

    async def generate_press_release(self, book: Book, news_hook: str = "") -> str:
        """Generate a press release about a book or author news."""
        prompt = f"""Write a professional press release:

Book: {book.title} by {AUTHOR.name}
Genre: {book.genre}
Description: {book.description}
News Hook: {news_hook or f'New release of {book.title}, a {book.genre} novel'}
Author: {AUTHOR.bio_short}
Contact: {AUTHOR.website}

Follow AP style press release format:
- Dateline
- Compelling headline
- Strong lead paragraph
- Supporting details
- Author bio boilerplate
- Contact information"""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=LITERARY_AGENT_SYSTEM_PROMPT,
            max_tokens=1200,
            temperature=0.5,
        )

    async def generate_library_request(self, book: Book, library_name: str) -> str:
        """Generate a library acquisition request letter."""
        prompt = f"""Write a polite, professional letter requesting that a library consider
adding this book to their collection:

Book: {book.title} by {AUTHOR.name}
Genre: {book.genre}
Description: {book.description}
Library: {library_name}
Author credentials: {AUTHOR.bio_short}

The letter should:
- Be addressed to the acquisitions department
- Explain why the book would be valuable for their patrons
- Mention the author's scientific credentials for credibility
- Be concise (200-250 words)
- Include where the book can be ordered"""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=LITERARY_AGENT_SYSTEM_PROMPT,
            max_tokens=600,
            temperature=0.5,
        )

    async def generate_forum_comment(
        self, context: str, book: Optional[Book] = None
    ) -> str:
        """Generate a natural forum comment that adds value."""
        book_ref = ""
        if book:
            book_ref = f"\nIf naturally relevant, you can mention '{book.title}' by {AUTHOR.name}, but ONLY if it genuinely fits the discussion."

        prompt = f"""You're participating in an online book/sci-fi forum discussion.
The thread context is:

{context}

Write a thoughtful, genuine comment (100-200 words) that:
- Adds value to the discussion
- Shows deep knowledge of the genre
- Is conversational, not promotional
- Doesn't sound like a bot or marketer
{book_ref}

The comment should feel like it's from an avid reader who happens to know a lot about science fiction and technology."""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=LITERARY_AGENT_SYSTEM_PROMPT,
            max_tokens=400,
            temperature=0.85,
        )

    async def generate_discussion_guide(self, book: Book) -> str:
        """Generate a book club discussion guide."""
        prompt = f"""Create a book club discussion guide for:

Title: {book.title}
Genre: {book.genre}
Description: {book.description}

Include:
- 8-10 thought-provoking discussion questions
- Thematic connections to current events
- Suggested paired readings
- An author context section mentioning the dual novelist-scientist career"""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=LITERARY_AGENT_SYSTEM_PROMPT,
            max_tokens=1500,
            temperature=0.7,
        )
