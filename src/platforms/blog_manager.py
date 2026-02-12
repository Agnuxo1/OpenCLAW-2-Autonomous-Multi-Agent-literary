"""Blog content management — generates and publishes blog posts."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BlogManager:
    """Manages blog content generation and static site publishing."""

    def __init__(self, blog_dir: str = "./state/blog"):
        self.blog_dir = Path(blog_dir)
        self.blog_dir.mkdir(parents=True, exist_ok=True)
        self.posts_dir = self.blog_dir / "posts"
        self.posts_dir.mkdir(exist_ok=True)

    async def create_post(
        self,
        title: str,
        content: str,
        tags: List[str] = None,
        category: str = "general",
    ) -> str:
        """Create a markdown blog post."""
        slug = title.lower().replace(" ", "-").replace("'", "")[:60]
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}-{slug}.md"

        frontmatter = {
            "title": title,
            "date": date_str,
            "tags": tags or [],
            "category": category,
            "author": "Francisco Angulo de Lafuente",
        }

        post_content = f"""---
{json.dumps(frontmatter, indent=2)}
---

# {title}

{content}

---

*Written by Francisco Angulo de Lafuente — [OpenCLAW](https://openclaw.ai/) | [GitHub](https://github.com/Agnuxo1)*
"""

        filepath = self.posts_dir / filename
        filepath.write_text(post_content, encoding="utf-8")
        logger.info(f"Blog post created: {filename}")
        return str(filepath)

    async def list_posts(self) -> List[Dict]:
        """List all blog posts."""
        posts = []
        for f in sorted(self.posts_dir.glob("*.md"), reverse=True):
            posts.append({
                "filename": f.name,
                "path": str(f),
                "size": f.stat().st_size,
            })
        return posts

    async def generate_index(self) -> str:
        """Generate an index page for the blog."""
        posts = await self.list_posts()
        index_lines = ["# OpenCLAW Literary Blog\n", "## Posts\n"]
        for p in posts:
            name = p["filename"].replace(".md", "").replace("-", " ").title()
            index_lines.append(f"- [{name}]({p['filename']})")
        index_content = "\n".join(index_lines)
        index_path = self.blog_dir / "index.md"
        index_path.write_text(index_content, encoding="utf-8")
        return str(index_path)
