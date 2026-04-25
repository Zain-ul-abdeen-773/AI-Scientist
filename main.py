"""
The AI Scientist — Main Entry Point
=====================================
Launches the Gradio web application for generating
complete, operationally-grounded experiment plans
from scientific hypotheses.

Hack-Nation × World Bank Youth Summit · Global AI Hackathon 2026

Usage:
    python main.py
    python main.py --port 8080
    python main.py --share
"""

import sys
import argparse
from pathlib import Path

# Ensure project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import get_config
from utils.logger import setup_logger
from app import create_app
from loguru import logger


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="The AI Scientist — Experiment Plan Generator"
    )
    parser.add_argument(
        "--port", type=int, default=7860,
        help="Server port (default: 7860)"
    )
    parser.add_argument(
        "--share", action="store_true",
        help="Create a public Gradio share link"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug logging"
    )
    return parser.parse_args()


def main():
    """Launch The AI Scientist application."""
    args = parse_args()

    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logger(log_level)

    logger.info("=" * 60)
    logger.info("  🔬 The AI Scientist — Starting Up")
    logger.info("=" * 60)

    # Load configuration
    config = get_config()
    config.ui.server_port = args.port
    config.ui.share = args.share

    # Check LLM availability
    llm_status = {
        "Groq": bool(config.llm.groq_api_key),
        "Gemini": bool(config.llm.gemini_api_key),
        "OpenAI": bool(config.llm.openai_api_key),
    }

    has_llm = any(llm_status.values())
    for name, available in llm_status.items():
        icon = "✅" if available else "❌"
        logger.info(f"  {icon} {name}")

    if not has_llm:
        logger.warning(
            "⚠️  No LLM API keys found! Set at least one in .env:\n"
            "    GROQ_API_KEY — Free at https://console.groq.com\n"
            "    GEMINI_API_KEY — Free at https://aistudio.google.com\n"
            "    OPENAI_API_KEY — Paid at https://platform.openai.com\n"
            "  Literature QC will still work, but plan generation needs an LLM."
        )

    # Create and launch app
    app = create_app(config)

    logger.info(f"🌐 Launching on port {config.ui.server_port}")
    logger.info(f"🔗 Open: http://localhost:{config.ui.server_port}")

    # Get theme/css attached by create_app
    theme = getattr(app, "_custom_theme", None)
    css = getattr(app, "_custom_css", None)

    app.launch(
        server_name=config.ui.server_name,
        server_port=config.ui.server_port,
        share=config.ui.share,
        show_error=True,
        theme=theme,
        css=css,
    )


if __name__ == "__main__":
    main()
