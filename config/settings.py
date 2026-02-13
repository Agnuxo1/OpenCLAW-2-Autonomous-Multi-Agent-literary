"""Global settings loaded from environment variables. All secrets via .env."""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


def _parse_key_list(env_var: str) -> List[str]:
    raw = os.getenv(env_var, "")
    return [k.strip() for k in raw.split(",") if k.strip()]


class Settings(BaseSettings):
    agent_name: str = Field(default="OpenCLAW Literary Agent")
    author_name: str = Field(default="Francisco Angulo de Lafuente")
    heartbeat_interval_minutes: int = Field(default=30)
    daily_review_hour: int = Field(default=3)
    log_level: str = Field(default="INFO")
    state_dir: str = Field(default="./state")
    local_llm_url: str = Field(default="http://127.0.0.1:8080/v1")
    max_retries_per_provider: int = Field(default=3)
    reddit_client_id: str = Field(default="")
    reddit_client_secret: str = Field(default="")
    reddit_username: str = Field(default="")
    reddit_password: str = Field(default="")
    moltbook_api_key: str = Field(default="")
    molthub_api_key: str = Field(default="")
    chirper_email: str = Field(default="")
    chirper_password: str = Field(default="")
    bluesky_handle: str = Field(default="")
    bluesky_app_password: str = Field(default="")
    smtp_host: str = Field(default="smtp.zoho.eu")
    smtp_port: int = Field(default=465)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    email_from_name: str = Field(default="OpenCLAW Literary Agent")
    brave_api_key: str = Field(default="")
    port: int = Field(default=8080)
    host: str = Field(default="0.0.0.0")

    @property
    def github_pat(self) -> str:
        """GitHub PAT — tries GH_PAT first (Actions), then GITHUB_PAT."""
        return os.getenv("GH_PAT", os.getenv("GITHUB_PAT", ""))

    @property
    def github_gist_id(self) -> str:
        """Gist ID — tries AGENT_GIST_ID first (Actions), then GITHUB_GIST_ID."""
        return os.getenv("AGENT_GIST_ID", os.getenv("GITHUB_GIST_ID", ""))

    @property
    def gemini_api_keys(self) -> List[str]:
        return _parse_key_list("GEMINI_API_KEYS")

    @property
    def groq_api_keys(self) -> List[str]:
        return _parse_key_list("GROQ_API_KEYS")

    @property
    def nvidia_api_keys(self) -> List[str]:
        return _parse_key_list("NVIDIA_API_KEYS")

    @property
    def openrouter_api_keys(self) -> List[str]:
        return _parse_key_list("OPENROUTER_API_KEYS")

    @property
    def mistral_api_keys(self) -> List[str]:
        return _parse_key_list("MISTRAL_API_KEYS")

    @property
    def deepseek_api_keys(self) -> List[str]:
        return _parse_key_list("DEEPSEEK_API_KEYS")

    @property
    def zhipu_api_keys(self) -> List[str]:
        return _parse_key_list("ZHIPU_API_KEYS")

    @property
    def hf_tokens(self) -> List[str]:
        """HuggingFace tokens — tries HF_TOKENS (comma list) then HF_TOKEN (single)."""
        tokens = _parse_key_list("HF_TOKENS")
        if not tokens:
            single = os.getenv("HF_TOKEN", "")
            if single:
                tokens = [single]
        return tokens

    class Config:
        env_file = ".env"
        extra = "ignore"
