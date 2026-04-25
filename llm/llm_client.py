"""
LLM Client — Unified Interface for Multiple LLM Providers
==========================================================
Supports Groq, Google Gemini, and OpenAI with automatic
fallback. Tries providers in order of preference until
one succeeds.

Usage:
    client = LLMClient(config)
    response = client.generate("Your prompt here")
"""

import time
from typing import Optional, List, Dict
from loguru import logger


class LLMClient:
    """
    Unified LLM client with multi-provider fallback.

    Provider priority: Groq → Gemini → OpenAI
    Automatically skips providers without valid API keys.
    """

    def __init__(self, config):
        """
        Initialize LLM client with configuration.

        Args:
            config: LLMConfig dataclass with API keys and model settings
        """
        self.config = config
        self._providers = []         # List of (name, callable) in priority order
        self._active_provider = None # Currently working provider name

        # Register available providers based on API keys
        self._register_providers()

        if not self._providers:
            logger.warning(
                "No LLM API keys found! Set GROQ_API_KEY, "
                "GEMINI_API_KEY, or OPENAI_API_KEY in .env"
            )

    # ── Provider Registration ────────────────────────────────
    def _register_providers(self) -> None:
        """Register all providers that have valid API keys."""

        # 1. Groq (fastest, free tier)
        if self.config.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.config.groq_api_key)
                self._providers.append(("groq", client))
                logger.info(f"Groq registered (model: {self.config.groq_model})")
            except ImportError:
                logger.warning("groq package not installed: pip install groq")

        # 2. Google Gemini (free tier, good quality)
        if self.config.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.config.gemini_api_key)
                model = genai.GenerativeModel(self.config.gemini_model)
                self._providers.append(("gemini", model))
                logger.info(f"Gemini registered (model: {self.config.gemini_model})")
            except ImportError:
                logger.warning(
                    "google-generativeai not installed: "
                    "pip install google-generativeai"
                )

        # 3. OpenAI (paid, highest quality)
        if self.config.openai_api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.config.openai_api_key)
                self._providers.append(("openai", client))
                logger.info(f"OpenAI registered (model: {self.config.openai_model})")
            except ImportError:
                logger.warning("openai package not installed: pip install openai")

    # ── Generation Methods ───────────────────────────────────
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text using the best available LLM provider.

        Tries each registered provider in order. Falls back to
        the next provider if one fails.

        Args:
            prompt: User prompt / question
            system_prompt: Optional system instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Generated text response

        Raises:
            RuntimeError: If no providers are available or all fail
        """
        if not self._providers:
            return self._fallback_response(prompt)

        temp = temperature or self.config.temperature
        tokens = max_tokens or self.config.max_tokens
        sys_prompt = system_prompt or ""

        # Try each provider in priority order
        for name, client in self._providers:
            try:
                logger.debug(f"Trying provider: {name}")
                result = self._call_provider(
                    name, client, prompt, sys_prompt, temp, tokens
                )
                self._active_provider = name
                return result

            except Exception as e:
                logger.warning(f"{name} failed: {e}")
                continue

        # All providers failed
        logger.error("All LLM providers failed")
        return self._fallback_response(prompt)

    def _call_provider(
        self,
        name: str,
        client,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Call a specific LLM provider.

        Args:
            name: Provider name (groq, gemini, openai)
            client: Provider SDK client instance
            prompt: User prompt
            system_prompt: System instruction
            temperature: Sampling temperature
            max_tokens: Maximum output tokens

        Returns:
            Generated text
        """
        if name == "groq":
            return self._call_groq(
                client, prompt, system_prompt, temperature, max_tokens
            )
        elif name == "gemini":
            return self._call_gemini(
                client, prompt, system_prompt, temperature, max_tokens
            )
        elif name == "openai":
            return self._call_openai(
                client, prompt, system_prompt, temperature, max_tokens
            )
        else:
            raise ValueError(f"Unknown provider: {name}")

    def _call_groq(
        self, client, prompt, system_prompt, temperature, max_tokens
    ) -> str:
        """Generate with Groq (LLaMA-3 70B)."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.config.groq_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def _call_gemini(
        self, model, prompt, system_prompt, temperature, max_tokens
    ) -> str:
        """Generate with Google Gemini."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )
        return response.text

    def _call_openai(
        self, client, prompt, system_prompt, temperature, max_tokens
    ) -> str:
        """Generate with OpenAI (GPT-4o-mini)."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.config.openai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def _fallback_response(self, prompt: str) -> str:
        """
        Return a helpful message when no LLM is available.
        This allows the app to still demonstrate the UI flow.
        """
        return (
            "⚠️ **No LLM API key configured.**\n\n"
            "To generate experiment plans, set at least one API key "
            "in the `.env` file:\n\n"
            "- `GROQ_API_KEY` — Free at https://console.groq.com\n"
            "- `GEMINI_API_KEY` — Free at https://aistudio.google.com\n"
            "- `OPENAI_API_KEY` — Paid at https://platform.openai.com\n\n"
            f"**Your query was:** {prompt[:200]}..."
        )

    # ── Status ───────────────────────────────────────────────
    @property
    def is_available(self) -> bool:
        """Check if at least one LLM provider is configured."""
        return len(self._providers) > 0

    @property
    def provider_name(self) -> str:
        """Return the name of the active/first provider."""
        if self._active_provider:
            return self._active_provider
        return self._providers[0][0] if self._providers else "none"

    def status(self) -> Dict[str, bool]:
        """Return availability status of each provider."""
        return {
            "groq": bool(self.config.groq_api_key),
            "gemini": bool(self.config.gemini_api_key),
            "openai": bool(self.config.openai_api_key),
        }
