"""
LLM Provider Pool with Circular Rotation
==========================================
Manages multiple LLM providers (Gemini, Groq, NVIDIA, ZhipuAI, Local).
When one provider hits rate limits, automatically rotates to the next.
Each provider can have multiple API keys that also rotate.
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProviderType(str, Enum):
    GEMINI = "gemini"
    GROQ = "groq"
    NVIDIA = "nvidia"
    ZHIPU = "zhipu"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


@dataclass
class ProviderKey:
    key: str
    provider: ProviderType
    last_used: float = 0
    fail_count: int = 0
    cooldown_until: float = 0
    total_calls: int = 0
    total_tokens: int = 0


@dataclass
class ProviderConfig:
    provider_type: ProviderType
    base_url: str
    model: str
    keys: List[ProviderKey] = field(default_factory=list)
    current_key_idx: int = 0
    supports_streaming: bool = True
    max_tokens: int = 4096
    temperature: float = 0.7


class LLMPool:
    """
    Circular rotation pool for multiple LLM providers.
    Automatically handles rate limits, errors, and failover.
    """

    def __init__(self, settings):
        self.settings = settings
        self.providers: List[ProviderConfig] = []
        self.current_provider_idx: int = 0
        self._lock = asyncio.Lock()
        self._setup_providers()

    def _setup_providers(self):
        """Initialize all available providers from settings."""

        # Gemini
        gemini_keys = self.settings.gemini_api_keys
        if gemini_keys:
            self.providers.append(ProviderConfig(
                provider_type=ProviderType.GEMINI,
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",
                keys=[ProviderKey(k, ProviderType.GEMINI) for k in gemini_keys],
            ))

        # Groq
        groq_keys = self.settings.groq_api_keys
        if groq_keys:
            self.providers.append(ProviderConfig(
                provider_type=ProviderType.GROQ,
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.3-70b-versatile",
                keys=[ProviderKey(k, ProviderType.GROQ) for k in groq_keys],
            ))

        # NVIDIA
        nvidia_keys = self.settings.nvidia_api_keys
        if nvidia_keys:
            self.providers.append(ProviderConfig(
                provider_type=ProviderType.NVIDIA,
                base_url="https://integrate.api.nvidia.com/v1",
                model="meta/llama-3.1-70b-instruct",
                keys=[ProviderKey(k, ProviderType.NVIDIA) for k in nvidia_keys],
            ))

        # ZhipuAI
        zhipu_keys = self.settings.zhipu_api_keys
        if zhipu_keys:
            self.providers.append(ProviderConfig(
                provider_type=ProviderType.ZHIPU,
                base_url="https://open.bigmodel.cn/api/paas/v4",
                model="glm-4-plus",
                keys=[ProviderKey(k, ProviderType.ZHIPU) for k in zhipu_keys],
            ))

        # Local LLM (always available as final fallback)
        if self.settings.local_llm_url:
            self.providers.append(ProviderConfig(
                provider_type=ProviderType.LOCAL,
                base_url=self.settings.local_llm_url,
                model="local",
                keys=[ProviderKey("local", ProviderType.LOCAL)],
            ))

        logger.info(
            f"LLM Pool initialized: {len(self.providers)} providers, "
            f"{sum(len(p.keys) for p in self.providers)} total keys"
        )
        for p in self.providers:
            logger.info(f"  → {p.provider_type.value}: {len(p.keys)} key(s), model={p.model}")

    def _get_next_provider(self) -> Optional[ProviderConfig]:
        """Get next available provider in circular order."""
        if not self.providers:
            return None

        now = time.time()
        attempts = 0
        while attempts < len(self.providers):
            provider = self.providers[self.current_provider_idx]
            # Check if any key is available
            available_keys = [
                k for k in provider.keys if k.cooldown_until < now
            ]
            if available_keys:
                return provider
            self.current_provider_idx = (self.current_provider_idx + 1) % len(self.providers)
            attempts += 1

        return None

    def _get_next_key(self, provider: ProviderConfig) -> Optional[ProviderKey]:
        """Get next available key for a provider."""
        now = time.time()
        attempts = 0
        while attempts < len(provider.keys):
            key = provider.keys[provider.current_key_idx]
            if key.cooldown_until < now:
                return key
            provider.current_key_idx = (provider.current_key_idx + 1) % len(provider.keys)
            attempts += 1
        return None

    def _rotate_key(self, provider: ProviderConfig):
        """Move to next key in this provider."""
        provider.current_key_idx = (provider.current_key_idx + 1) % len(provider.keys)

    def _rotate_provider(self):
        """Move to next provider."""
        self.current_provider_idx = (self.current_provider_idx + 1) % len(self.providers)

    def _mark_key_failed(self, key: ProviderKey, cooldown_seconds: int = 60):
        """Put a key on cooldown after failure."""
        key.fail_count += 1
        key.cooldown_until = time.time() + cooldown_seconds
        logger.warning(
            f"Key for {key.provider.value} on cooldown for {cooldown_seconds}s "
            f"(fail #{key.fail_count})"
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2048,
        temperature: float = 0.7,
        retries: int = 0,
    ) -> str:
        """
        Generate text using the LLM pool with automatic failover.
        Tries current provider/key, rotates on failure.
        """
        max_total_retries = self.settings.max_retries_per_provider * max(len(self.providers), 1) * 2

        async with self._lock:
            for attempt in range(max_total_retries):
                provider = self._get_next_provider()
                if not provider:
                    logger.error("All providers exhausted. Waiting 60s...")
                    await asyncio.sleep(60)
                    continue

                key = self._get_next_key(provider)
                if not key:
                    self._rotate_provider()
                    continue

                try:
                    result = await self._call_provider(
                        provider, key, prompt, system_prompt, max_tokens, temperature
                    )
                    key.last_used = time.time()
                    key.total_calls += 1
                    key.fail_count = 0  # Reset on success
                    # Rotate key for next call (spread usage)
                    self._rotate_key(provider)
                    return result

                except Exception as e:
                    error_str = str(e).lower()
                    is_rate_limit = any(
                        x in error_str
                        for x in ["rate limit", "429", "quota", "too many", "resource_exhausted"]
                    )

                    if is_rate_limit:
                        # Longer cooldown for rate limits
                        self._mark_key_failed(key, cooldown_seconds=300)
                        self._rotate_key(provider)
                        # If all keys for this provider are on cooldown, rotate provider
                        if not self._get_next_key(provider):
                            self._rotate_provider()
                            logger.info(f"All keys for {provider.provider_type.value} exhausted, rotating provider")
                    else:
                        self._mark_key_failed(key, cooldown_seconds=30)
                        self._rotate_key(provider)

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_total_retries} failed "
                        f"({provider.provider_type.value}): {e}"
                    )

        raise RuntimeError("All LLM providers and keys exhausted after maximum retries")

    async def _call_provider(
        self,
        provider: ProviderConfig,
        key: ProviderKey,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Dispatch to the appropriate provider API."""
        if provider.provider_type == ProviderType.GEMINI:
            return await self._call_gemini(key.key, prompt, system_prompt, max_tokens, temperature)
        elif provider.provider_type in (ProviderType.GROQ, ProviderType.NVIDIA, ProviderType.LOCAL, ProviderType.HUGGINGFACE):
            return await self._call_openai_compatible(
                provider.base_url, key.key, provider.model,
                prompt, system_prompt, max_tokens, temperature
            )
        elif provider.provider_type == ProviderType.ZHIPU:
            return await self._call_zhipu(key.key, provider.model, prompt, system_prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider: {provider.provider_type}")

    async def _call_gemini(
        self, api_key: str, prompt: str, system_prompt: str,
        max_tokens: int, temperature: float,
    ) -> str:
        """Call Google Gemini API."""
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction=system_prompt if system_prompt else None,
        )
        response = await asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        return response.text

    async def _call_openai_compatible(
        self, base_url: str, api_key: str, model: str,
        prompt: str, system_prompt: str, max_tokens: int, temperature: float,
    ) -> str:
        """Call any OpenAI-compatible API (Groq, NVIDIA, Local)."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content

    async def _call_zhipu(
        self, api_key: str, model: str, prompt: str,
        system_prompt: str, max_tokens: int, temperature: float,
    ) -> str:
        """Call ZhipuAI (GLM) API."""
        from zhipuai import ZhipuAI

        client = ZhipuAI(api_key=api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def get_status(self) -> Dict[str, Any]:
        """Return pool status for monitoring."""
        now = time.time()
        status = {"providers": [], "total_calls": 0}
        for p in self.providers:
            provider_info = {
                "type": p.provider_type.value,
                "model": p.model,
                "keys": []
            }
            for k in p.keys:
                key_info = {
                    "available": k.cooldown_until < now,
                    "total_calls": k.total_calls,
                    "fail_count": k.fail_count,
                }
                if k.cooldown_until > now:
                    key_info["cooldown_remaining"] = int(k.cooldown_until - now)
                provider_info["keys"].append(key_info)
                status["total_calls"] += k.total_calls
            status["providers"].append(provider_info)
        return status
