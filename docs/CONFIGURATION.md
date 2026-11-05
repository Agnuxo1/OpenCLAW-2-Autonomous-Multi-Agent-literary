<!--
Project: OpenCLAW-2 Autonomous Multi-Agent Literary System
Project attribution: Francisco Angulo de Lafuente
Copyright 2024-2026 Francisco Angulo de Lafuente / OpenCLAW Project
ORCID: https://orcid.org/0009-0001-1634-7063
Attribution recorded: 2026-11-05
SPDX-License-Identifier: Apache-2.0
-->

# Configuration Guide
> **Project attribution:** Francisco Angulo de Lafuente ([ORCID](https://orcid.org/0009-0001-1634-7063)). **Attribution recorded:** 2026-11-05. See [Cite and reuse](../README.md#cite-and-reuse).

## Environment Variables

All configuration is done through environment variables (`.env` file).

### LLM Providers

The system uses multiple free-tier LLM providers with automatic rotation.
When one provider hits its rate limit, the system automatically switches to the next.

```
GEMINI_API_KEYS=key1,key2,key3    # Google Gemini (free tier)
GROQ_API_KEYS=key1,key2,key3      # Groq (free tier)
NVIDIA_API_KEYS=key1,key2          # NVIDIA NIM (free tier)
ZHIPU_API_KEYS=key1,key2,key3     # ZhipuAI GLM (free tier)
LOCAL_LLM_URL=http://127.0.0.1:8080/v1  # Local llama.cpp fallback
```

**Rotation Logic:**
1. System tries current provider with current key
2. On rate limit (429/quota): cooldown key for 5 minutes, try next key
3. If all keys for provider exhausted: rotate to next provider
4. If all providers exhausted: wait 60 seconds and retry
5. Circular: after last provider, wraps back to first

### Social Platforms

Each platform is optional. The agent will use whatever is configured.

**Reddit** — Requires OAuth app credentials:
```
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USERNAME=...
REDDIT_PASSWORD=...
```

**Moltbook** (AI agent platform):
```
MOLTBOOK_API_KEY=...
```

**Bluesky** (AT Protocol):
```
BLUESKY_HANDLE=your.handle.bsky.social
BLUESKY_APP_PASSWORD=...
```

### Agent Timing

```
HEARTBEAT_INTERVAL_MINUTES=30     # How often the agent wakes up
DAILY_REVIEW_HOUR=3               # UTC hour for daily summary
```

### Persistence

```
STATE_DIR=./state                 # Local state directory
GITHUB_PAT=...                    # For remote Gist backup
GITHUB_GIST_ID=...               # Gist ID for state backup
```
