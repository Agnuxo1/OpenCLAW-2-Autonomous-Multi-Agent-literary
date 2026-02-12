"""
Author profile and book catalog for Francisco Angulo de Lafuente.
Used by all agents for content generation and marketing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Book:
    title: str
    genre: str
    year: int
    language: str
    description: str
    isbn: str = ""
    buy_links: Dict[str, str] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    series: str = ""
    awards: List[str] = field(default_factory=list)


@dataclass
class AuthorProfile:
    name: str = "Francisco Angulo de Lafuente"
    bio_short: str = (
        "Francisco Angulo de Lafuente is a prolific Spanish author and independent AI researcher "
        "with over 34 published novels spanning science fiction, thriller, dystopia, and historical "
        "fiction. Also the founder of OpenCLAW (Open Collaborative Laboratory for Autonomous Wisdom), "
        "his work explores the intersection of technology, human consciousness, and the future of civilization."
    )
    bio_long: str = (
        "Francisco Angulo de Lafuente is a visionary author and scientist whose literary work has "
        "explored the frontiers of technology and humanity since 2006. With over 34 novels published "
        "across genres including cyberpunk, apocalyptic sci-fi, psychological thriller, and historical "
        "drama, his fiction consistently anticipates real-world technological developments. His novel "
        "'ApocalipsIA' (2024) explores post-AGI society, while 'GENESIS IA' imagines superintelligent "
        "systems — themes he also researches professionally as the founder of OpenCLAW. His scientific "
        "publications on neuromorphic computing and physics-based AI architectures appear on ArXiv and "
        "Google Scholar, giving his fiction an unusual depth of technical authenticity. Writing in both "
        "Spanish and English, his work is available worldwide through Apple Books, Amazon, Barnes & Noble, "
        "and other major retailers."
    )
    nationality: str = "Spanish"
    languages: List[str] = field(default_factory=lambda: ["Spanish", "English"])
    website: str = "https://openclaw.ai/"
    github: str = "https://github.com/Agnuxo1"
    scholar: str = "https://scholar.google.com/citations?user=6nOpJ9IAAAAJ&hl=es"
    arxiv: str = "https://arxiv.org/search/cs?searchtype=author&query=de+Lafuente,+F+A"
    wikipedia: str = "https://es.wikipedia.org/wiki/Francisco_Angulo_de_Lafuente"

    genres: List[str] = field(default_factory=lambda: [
        "Science Fiction", "Cyberpunk", "Dystopia", "Thriller",
        "Psychological Thriller", "Historical Fiction", "Gothic Suspense",
        "Space Opera", "Apocalyptic Fiction", "Techno-thriller"
    ])

    unique_selling_points: List[str] = field(default_factory=lambda: [
        "Dual expertise: published novelist AND active AI researcher",
        "Fiction informed by real scientific work in neuromorphic computing",
        "34+ novels spanning 20 years of consistent creative output",
        "Bilingual author (Spanish/English) with global reach",
        "Predicted AI developments in fiction before they happened",
        "Founder of OpenCLAW — bridging AI research and literary arts",
    ])

    comparable_authors: List[str] = field(default_factory=lambda: [
        "Isaac Asimov (scientist-author dual career)",
        "Philip K. Dick (reality-questioning sci-fi)",
        "Michael Crichton (tech-thriller with scientific depth)",
        "Liu Cixin (hard sci-fi with civilizational scope)",
        "William Gibson (cyberpunk visionary)",
    ])


# === ENGLISH NOVELS CATALOG ===

ENGLISH_NOVELS: List[Book] = [
    Book(
        title="Kira and the Ice Storm",
        genre="Apocalyptic Science Fiction",
        year=2009,
        language="English",
        description=(
            "In a world gripped by catastrophic climate collapse, Kira must navigate "
            "a frozen wasteland where survival depends on ingenuity, courage, and "
            "the fragile bonds of human connection. A visceral exploration of humanity's "
            "resilience against nature's ultimate test."
        ),
        buy_links={"Apple Books": "https://books.apple.com/book/kira-and-the-ice-storm/"},
        keywords=["climate fiction", "survival", "apocalypse", "ice age", "dystopia"],
    ),
    Book(
        title="Star Wind: The Pyramid of Destiny",
        genre="Epic Space Opera",
        year=2015,
        language="English",
        description=(
            "An interstellar epic where ancient alien artifacts hold the key to "
            "humanity's next evolutionary leap. When a deep-space expedition discovers "
            "a pyramid structure broadcasting signals across dimensions, the crew must "
            "confront forces that challenge everything they know about reality."
        ),
        buy_links={"Barnes & Noble": "https://www.barnesandnoble.com/"},
        keywords=["space opera", "alien artifacts", "interstellar", "pyramid", "destiny"],
    ),
    Book(
        title="The Obituarist",
        genre="Gothic Suspense",
        year=2025,
        language="English",
        description=(
            "A biographer who specializes in writing the lives of the recently deceased "
            "stumbles upon a pattern that suggests his subjects didn't die naturally. "
            "As he digs deeper, the line between chronicler and detective blurs — and "
            "the dead seem to have secrets that could kill."
        ),
        buy_links={"Apple Books": "https://books.apple.com/book/the-obituarist/"},
        keywords=["gothic", "suspense", "mystery", "biography", "dark fiction"],
    ),
    Book(
        title="The Forgotten Tomb",
        genre="Archaeological Thriller",
        year=2025,
        language="English",
        description=(
            "An archaeological discovery in the Iberian Peninsula reveals a tomb that "
            "shouldn't exist — its technology predates known civilization by millennia. "
            "A race against rival factions, government agencies, and time itself unfolds "
            "as the tomb's secrets threaten to rewrite human history."
        ),
        buy_links={"Apple Books": "https://books.apple.com/book/the-forgotten-tomb/"},
        keywords=["archaeology", "thriller", "ancient mystery", "conspiracy", "Iberian Peninsula"],
    ),
    Book(
        title="Freak",
        genre="Psychological Science Fiction",
        year=2023,
        language="English",
        description=(
            "What happens when the boundary between human consciousness and artificial "
            "intelligence dissolves? A psychological deep-dive into identity, perception, "
            "and what it means to be 'normal' in a world where minds can be edited."
        ),
        buy_links={
            "Amazon": "https://www.amazon.com/",
            "Walmart": "https://www.walmart.com/",
        },
        keywords=["AI consciousness", "psychological", "identity", "transhumanism"],
    ),
    Book(
        title="Summer of 1989",
        genre="Cold War Historical Drama",
        year=2024,
        language="English",
        description=(
            "Set against the fall of the Berlin Wall, this intimate drama follows "
            "interconnected lives on both sides of the Iron Curtain during the summer "
            "that changed everything. Love, betrayal, and hope collide as an era ends."
        ),
        keywords=["Cold War", "Berlin Wall", "1989", "historical fiction", "drama"],
    ),
    Book(
        title="Solie",
        genre="Futuristic Science Fiction / Drama",
        year=2024,
        language="English",
        description=(
            "In a near-future where AI companions have become indistinguishable from "
            "humans, Solie — a synthetic being — begins to question the nature of her "
            "own existence. A poignant exploration of consciousness, love, and the "
            "meaning of being alive."
        ),
        keywords=["AI companion", "consciousness", "near future", "existential", "drama"],
    ),
    Book(
        title="4 Days of 4 Years",
        genre="Psychological Thriller",
        year=2024,
        language="English",
        description=(
            "A fragmented temporal structure reveals four pivotal days spread across "
            "four years, each holding a piece of a devastating truth. A masterclass "
            "in unreliable narration where nothing — and no one — is what they seem."
        ),
        keywords=["psychological thriller", "time structure", "unreliable narrator", "suspense"],
    ),
]

# === SPANISH NOVELS (for reference/bilingual marketing) ===

SPANISH_NOVELS: List[Book] = [
    Book(title="La Reliquia", genre="Satirical Sci-Fi", year=2006, language="Spanish",
         description="Science fiction with a satirical edge, exploring technology and society.",
         buy_links={"Apple Books": "https://books.apple.com/"}),
    Book(title="Shanghai 3", genre="Cyberpunk Dystopia", year=2015, language="Spanish",
         description="A cyberpunk vision of a hyper-connected future Shanghai."),
    Book(title="El Código del Caos", genre="Techno-thriller", year=2016, language="Spanish",
         description="A technological thriller where chaos theory meets digital espionage."),
    Book(title="ApocalipsIA – El día después de la AGI", genre="AI Dystopia", year=2024,
         language="Spanish",
         description="What happens the day after Artificial General Intelligence arrives? A prophetic novel."),
    Book(title="GÉNESIS IA: Super Inteligencia Artificial", genre="AI Science Fiction",
         year=2024, language="Spanish",
         description="Advanced AI fiction exploring superintelligence emergence.",
         buy_links={"Amazon": "https://www.amazon.com/"}),
    Book(title="El experimento cuántico", genre="Scientific Thriller", year=2025,
         language="Spanish",
         description="A thriller built on quantum paradoxes and temporal anomalies."),
    Book(title="El biógrafo de difuntos", genre="Gothic Suspense", year=2025,
         language="Spanish",
         description="Original Spanish version of The Obituarist."),
    Book(title="La tumba olvidada", genre="Archaeological Thriller", year=2025,
         language="Spanish",
         description="Original Spanish version of The Forgotten Tomb."),
    Book(title="El vampiro del Metropolitan", genre="Urban Horror", year=2025,
         language="Spanish",
         description="Contemporary urban terror in a world-famous museum."),
    Book(title="Preparacionismo – El último superviviente", genre="Survival Fiction",
         year=2025, language="Spanish",
         description="Strategic survival fiction for the modern prepper mindset.",
         buy_links={"Agapea": "https://www.agapea.com/"}),
]

ALL_BOOKS = ENGLISH_NOVELS + SPANISH_NOVELS
AUTHOR = AuthorProfile()


def get_english_novels() -> List[Book]:
    return ENGLISH_NOVELS


def get_featured_book() -> Book:
    """Return the most recent or most promotable English novel."""
    import random
    recent = [b for b in ENGLISH_NOVELS if b.year >= 2024]
    return random.choice(recent) if recent else random.choice(ENGLISH_NOVELS)
