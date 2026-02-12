"""Tests for LLM Pool rotation logic."""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock


def test_imports():
    """Verify all modules can be imported."""
    from config.settings import Settings
    from config.author_profile import AUTHOR, ENGLISH_NOVELS, get_featured_book
    from src.utils.llm_pool import LLMPool, ProviderType
    from src.utils.logger import get_logger
    from src.memory.persistent_state import PersistentState
    from src.marketing.content_generator import ContentGenerator
    from src.agents.marketing_agent import MarketingAgent
    from src.agents.submissions_agent import SubmissionsAgent
    from src.agents.community_agent import CommunityAgent
    from src.agents.library_agent import LibraryAgent
    from src.agents.orchestrator import Orchestrator
    from src.self_improvement.strategy_reflector import StrategyReflector
    assert True


def test_author_profile():
    """Verify author profile data."""
    from config.author_profile import AUTHOR, ENGLISH_NOVELS, get_featured_book

    assert AUTHOR.name == "Francisco Angulo de Lafuente"
    assert len(ENGLISH_NOVELS) >= 8
    assert all(b.language == "English" for b in ENGLISH_NOVELS)

    featured = get_featured_book()
    assert featured.title
    assert featured.genre


def test_provider_types():
    """Verify provider enum."""
    from src.utils.llm_pool import ProviderType

    assert ProviderType.GEMINI.value == "gemini"
    assert ProviderType.GROQ.value == "groq"
    assert ProviderType.LOCAL.value == "local"


def test_settings_defaults():
    """Verify settings defaults."""
    import os
    # Clear any existing env vars for clean test
    from config.settings import Settings
    s = Settings()
    assert s.heartbeat_interval_minutes == 30
    assert s.author_name == "Francisco Angulo de Lafuente"
