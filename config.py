"""
The AI Scientist — Centralized Configuration
=============================================
All API keys, model settings, paths, and search parameters
in one place. Uses dataclasses for clean, type-safe config.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

# ── Load environment variables from .env ─────────────────────
load_dotenv()

# ── Project Paths ────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
FEEDBACK_DIR = DATA_DIR / "feedback"

# Ensure data directories exist
DATA_DIR.mkdir(exist_ok=True)
FEEDBACK_DIR.mkdir(exist_ok=True)


# ── LLM Configuration ───────────────────────────────────────
@dataclass
class LLMConfig:
    """Settings for LLM backends (Groq, Gemini, OpenAI)."""

    # API keys (loaded from environment)
    groq_api_key: str = field(
        default_factory=lambda: os.getenv("GROQ_API_KEY", "")
    )
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "")
    )
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )

    # Model names per provider
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-2.0-flash"
    openai_model: str = "gpt-4o-mini"

    # Generation parameters
    temperature: float = 0.3          # Low for factual, structured output
    max_tokens: int = 4096            # Enough for detailed plans
    timeout_seconds: int = 60         # API call timeout


# ── Literature Search Configuration ──────────────────────────
@dataclass
class LiteratureConfig:
    """Settings for ArXiv and Semantic Scholar search."""

    # ArXiv
    arxiv_base_url: str = "http://export.arxiv.org/api/query"
    arxiv_max_results: int = 10       # Papers to fetch per search
    arxiv_delay_seconds: float = 3.0  # Rate limit (ArXiv policy)

    # Semantic Scholar
    s2_base_url: str = "https://api.semanticscholar.org/graph/v1"
    s2_max_results: int = 10          # Papers to fetch per search
    s2_fields: List[str] = field(
        default_factory=lambda: [
            "title", "abstract", "year", "citationCount",
            "url", "authors", "externalIds",
        ]
    )

    # Novelty checking
    similarity_threshold_exact: float = 0.9     # Exact match
    similarity_threshold_similar: float = 0.5   # Similar work


# ── Planner Configuration ────────────────────────────────────
@dataclass
class PlannerConfig:
    """Settings for experiment plan generation."""

    # Plan sections to generate
    sections: List[str] = field(
        default_factory=lambda: [
            "protocol",
            "materials_and_budget",
            "timeline",
            "validation",
        ]
    )

    # Budget currency
    currency: str = "USD"
    currency_symbol: str = "$"


# ── Feedback Configuration ───────────────────────────────────
@dataclass
class FeedbackConfig:
    """Settings for the scientist feedback loop."""

    feedback_dir: Path = FEEDBACK_DIR
    max_few_shot_examples: int = 3    # Past corrections to inject
    min_similarity_score: float = 0.3 # Minimum relevance for retrieval


# ── UI Configuration ─────────────────────────────────────────
@dataclass
class UIConfig:
    """Settings for the Gradio web interface."""

    server_name: str = "0.0.0.0"
    server_port: int = 7860
    share: bool = False
    title: str = "🔬 The AI Scientist"
    theme: str = "soft"               # Gradio theme name


# ── Master Configuration ─────────────────────────────────────
@dataclass
class AppConfig:
    """Master configuration aggregating all sub-configs."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    literature: LiteratureConfig = field(default_factory=LiteratureConfig)
    planner: PlannerConfig = field(default_factory=PlannerConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    log_level: str = "INFO"


def get_config() -> AppConfig:
    """Factory function to create the default configuration."""
    return AppConfig()
