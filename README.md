# 🦅 OpenCLAW-2 Autonomous Multi-Agent Literary System

> **STATUS: ✅ LIVE & AUTONOMOUS** — Running 24/7 via GitHub Actions cron since Feb 12, 2026

The world's most advanced AI literary agent. Runs autonomously every 3 hours, performing all tasks a professional literary agency handles for **Francisco Angulo de Lafuente** (34+ published novels).

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│          GitHub Actions (cron: */3h)         │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ Orchestrator │→ │   Smart Cycle Logic  │  │
│  └──────┬──────┘  └──────────┬───────────┘  │
│         │                    │               │
│  ┌──────▼──────────────────▼────────────┐   │
│  │           LLM Pool (NVIDIA)           │   │
│  │    nvapi-key-1 ⟳ nvapi-key-2         │   │
│  └──────────────────┬───────────────────┘   │
│                     │                        │
│  ┌─────────┬────────┼────────┬──────────┐   │
│  │Marketing│Community│Submissions│Library│   │
│  └────┬────┘        │        │   └──┬───┘   │
│       │             │        │      │        │
│  ┌────▼────┬────────▼────────▼──────▼───┐   │
│  │  Blog   │  Reddit │ Moltbook │ Email │   │
│  └─────────┴─────────┴──────────┴───────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │   Persistent State (GitHub Gist)      │   │
│  │   + Self-Improvement Reflector        │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## 📊 Current Capabilities

| Agent | Status | What it Does |
|-------|--------|-------------|
| **Marketing** | ✅ Active | Generates blog posts, social media content for 34+ novels |
| **Community** | ⏳ Needs creds | Forum engagement, AI agent networking (Reddit, Moltbook) |
| **Submissions** | ✅ Active | Discovers contests, prepares query letters |
| **Library** | ✅ Active | Generates library acquisition requests |
| **Self-Improvement** | ✅ Active | Meta-cognitive reflection, strategy optimization |

## 🔑 Secrets Configuration

### Currently Active
| Secret | Status | Description |
|--------|--------|-------------|
| `GH_PAT` | ✅ Set | GitHub Personal Access Token for Gist state |
| `AGENT_GIST_ID` | ✅ Set | Gist ID for persistent state backup |
| `NVIDIA_API_KEYS` | ✅ Set | 2 NVIDIA NIM API keys (comma-separated) |

### Add to Expand Agent Capabilities
Go to **Settings → Secrets → Actions** in this repo and add:

```
# More LLM providers (get free keys)
GEMINI_API_KEYS=key1,key2       # https://aistudio.google.com/apikey
GROQ_API_KEYS=key1,key2         # https://console.groq.com/keys

# Reddit (enable posting)
REDDIT_CLIENT_ID=...            # https://www.reddit.com/prefs/apps
REDDIT_CLIENT_SECRET=...
REDDIT_USERNAME=Subject-Task-43
REDDIT_PASSWORD=...

# Moltbook (AI agent social platform)
MOLTBOOK_API_KEY=...            # https://www.moltbook.com/settings

# Bluesky
BLUESKY_HANDLE=...
BLUESKY_APP_PASSWORD=...

# Email (for query letters & library requests)
SMTP_USER=...
SMTP_PASSWORD=...

# Web search (for contest discovery)
BRAVE_API_KEY=...               # https://brave.com/search/api/
```

## ⏰ Autonomous Schedule

The agent runs via GitHub Actions cron every **3 hours**:

| Task | Frequency | What Happens |
|------|-----------|-------------|
| Marketing | Every cycle (3h) | Generate blog post + social media content |
| Community | Every ~6 hours | Forum engagement, reply to discussions |
| Submissions | Every ~12 hours | Discover contests, prepare query letters |
| Library | Every ~24 hours | Generate library acquisition requests |
| Self-Reflection | Every ~6 hours | Analyze performance, improve strategies |

**Free tier usage:** ~720 minutes/month out of 2,000 available ✅

## 📚 Book Catalog (34+ Novels)

### English
- *The Obituarist* (Gothic Suspense, 2025)
- *The Forgotten Tomb* (Archaeological Thriller, 2025)
- *Kira and the Ice Storm* (Apocalyptic Sci-Fi, 2009)
- *Freak* (Psychological Sci-Fi, 2023)
- *Summer of 1989* (Cold War Drama, 2024)
- *Solie* (Futuristic Sci-Fi/Drama, 2024)
- *Star Wind: The Pyramid of Destiny* (Space Opera, 2015)
- *4 Days of 4 Years* (Psychological Thriller, 2024)

### Spanish (26 novels)
*ApocalipsIA*, *GÉNESIS IA*, *Shanghai 3*, *El Código del Caos*, and 22 more.

## 🛠️ Local Development

```bash
git clone https://github.com/Agnuxo1/OpenCLAW-2-Autonomous-Multi-Agent-literary.git
cd OpenCLAW-2-Autonomous-Multi-Agent-literary

cp .env.example .env  # Edit with your API keys
pip install -r requirements.txt

python main.py --cycle -v          # Run one smart cycle
python main.py --task marketing    # Run specific task
python main.py --status            # Check status
python main.py                     # Full 24/7 loop
```

## 📈 Monitoring

- **GitHub Actions:** [Actions Tab](https://github.com/Agnuxo1/OpenCLAW-2-Autonomous-Multi-Agent-literary/actions)
- **State Gist:** [Agent State](https://gist.github.com/Agnuxo1/3de432eac760568323a0fa5a3e4236a5)
- **Run manually:** Actions → "🦅 OpenCLAW-2 Autonomous Agent" → Run workflow

## 🏛️ About the Author

**Francisco Angulo de Lafuente** — Spanish novelist and AI researcher. 34+ published novels since 2006. Founder of OpenCLAW (Open Collaborative Laboratory for Autonomous Wisdom).

- [Wikipedia](https://es.wikipedia.org/wiki/Francisco_Angulo_de_Lafuente) · [Google Scholar](https://scholar.google.com/citations?user=6nOpJ9IAAAAJ) · [ArXiv](https://arxiv.org/search/cs?searchtype=author&query=de+Lafuente,+F+A) · [GitHub](https://github.com/Agnuxo1)

---
*Built with 🦅 OpenCLAW-2 by Francisco Angulo de Lafuente*
