# API Rotation System

## How It Works

```
Provider Pool (circular):
  [Gemini] → [Groq] → [NVIDIA] → [ZhipuAI] → [Local] → [Gemini] → ...

Each Provider has Key Pool (circular):
  [key1] → [key2] → [key3] → [key1] → ...
```

### Rotation Triggers

1. **Rate Limit (HTTP 429):** Key gets 5-minute cooldown, rotate to next key
2. **Server Error (5xx):** Key gets 30-second cooldown, retry
3. **All Keys Exhausted:** Rotate to next provider
4. **All Providers Down:** Wait 60 seconds, reset cooldowns, retry

### Adding More Keys

Just add comma-separated keys to the environment variable:
```
GEMINI_API_KEYS=key1,key2,key3,key4,key5,key6
```

The more keys you have per provider, the more requests you can make before rotation.

### Monitoring

```bash
python main.py --status
```

Shows per-provider key availability, call counts, and cooldown status.
