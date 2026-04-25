"""
LLM Client — Unified Interface for Multiple LLM Providers
==========================================================
Supports Groq, Google Gemini, and OpenAI with automatic
fallback. Tries providers in order of preference until
one succeeds.

Improvements:
    - Response caching: repeated prompts return instantly
    - Retry with exponential backoff for transient failures
    - Thread-safe operation

Usage:
    client = LLMClient(config)
    response = client.generate("Your prompt here")
"""

import time
import hashlib
import threading
from typing import Optional, List, Dict
from loguru import logger


class LLMClient:
    """
    Unified LLM client with multi-provider fallback.

    Provider priority: Groq → Gemini → OpenAI
    Automatically skips providers without valid API keys.
    Includes response caching and retry logic.
    """

    # ── Cache settings ───────────────────────────────────────
    MAX_CACHE_SIZE = 100          # Max cached responses
    MAX_RETRIES = 3               # Retries per provider
    RETRY_BACKOFF_BASE = 2.0      # Exponential backoff base (seconds)

    def __init__(self, config):
        """
        Initialize LLM client with configuration.

        Args:
            config: LLMConfig dataclass with API keys and model settings
        """
        self.config = config
        self._providers = []         # List of (name, callable) in priority order
        self._active_provider = None # Currently working provider name

        # Response cache: hash(prompt+system) → response text
        self._cache: Dict[str, str] = {}
        self._cache_lock = threading.Lock()

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
                # Try new SDK first (google-genai)
                from google import genai
                client = genai.Client(api_key=self.config.gemini_api_key)
                self._providers.append(("gemini", client))
                self._gemini_sdk = "new"
                logger.info(f"Gemini registered via google-genai (model: {self.config.gemini_model})")
            except ImportError:
                try:
                    # Fallback to old SDK (deprecated)
                    import google.generativeai as genai_old
                    genai_old.configure(api_key=self.config.gemini_api_key)
                    model = genai_old.GenerativeModel(self.config.gemini_model)
                    self._providers.append(("gemini", model))
                    self._gemini_sdk = "old"
                    logger.info(f"Gemini registered via legacy SDK (model: {self.config.gemini_model})")
                except ImportError:
                    logger.warning(
                        "No Gemini SDK installed: "
                        "pip install google-genai"
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

    # ── Caching ──────────────────────────────────────────────
    def _cache_key(self, prompt: str, system_prompt: str) -> str:
        """Generate a deterministic cache key from prompt + system prompt."""
        combined = f"{system_prompt}||{prompt}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]

    def _get_cached(self, key: str) -> Optional[str]:
        """Retrieve a cached response (thread-safe)."""
        with self._cache_lock:
            return self._cache.get(key)

    def _set_cached(self, key: str, value: str) -> None:
        """Store a response in cache (thread-safe, with eviction)."""
        with self._cache_lock:
            # Evict oldest entries if cache is full
            if len(self._cache) >= self.MAX_CACHE_SIZE:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            self._cache[key] = value

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

        Features:
            - Checks cache first for repeated prompts
            - Tries each registered provider in order
            - Retries with exponential backoff on transient failures
            - Falls back to next provider if one fails permanently

        Args:
            prompt: User prompt / question
            system_prompt: Optional system instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Generated text response
        """
        if not self._providers:
            return self._fallback_response(prompt)

        temp = temperature or self.config.temperature
        tokens = max_tokens or self.config.max_tokens
        sys_prompt = system_prompt or ""

        # ── Check cache first ────────────────────────────────
        cache_key = self._cache_key(prompt, sys_prompt)
        cached = self._get_cached(cache_key)
        if cached:
            logger.debug("Cache hit — returning cached response")
            return cached

        # ── Try each provider with retry logic ───────────────
        for name, client in self._providers:
            result = self._try_provider_with_retries(
                name, client, prompt, sys_prompt, temp, tokens
            )
            if result is not None:
                self._active_provider = name
                self._set_cached(cache_key, result)
                return result

        # All providers failed
        logger.error("All LLM providers failed after retries")
        return self._fallback_response(prompt)

    def _try_provider_with_retries(
        self,
        name: str,
        client,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> Optional[str]:
        """
        Try a provider with exponential backoff retries.

        Args:
            name: Provider name
            client: SDK client
            prompt, system_prompt, temperature, max_tokens: Generation params

        Returns:
            Generated text or None if all retries exhausted
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.debug(f"Provider {name}: attempt {attempt}/{self.MAX_RETRIES}")
                result = self._call_provider(
                    name, client, prompt, system_prompt, temperature, max_tokens
                )
                return result

            except Exception as e:
                is_rate_limit = "429" in str(e) or "rate" in str(e).lower()
                is_last_attempt = attempt == self.MAX_RETRIES

                if is_rate_limit and not is_last_attempt:
                    # Exponential backoff for rate limits
                    wait = self.RETRY_BACKOFF_BASE ** attempt
                    logger.warning(
                        f"{name} rate-limited (attempt {attempt}), "
                        f"retrying in {wait:.1f}s..."
                    )
                    time.sleep(wait)
                elif is_last_attempt:
                    logger.warning(
                        f"{name} failed after {self.MAX_RETRIES} attempts: {e}"
                    )
                else:
                    # Non-retryable error — skip to next provider
                    logger.warning(f"{name} error (non-retryable): {e}")
                    break

        return None

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
        self, client, prompt, system_prompt, temperature, max_tokens
    ) -> str:
        """Generate with Google Gemini (supports new and old SDK)."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        if getattr(self, "_gemini_sdk", "old") == "new":
            # New SDK (google-genai)
            response = client.models.generate_content(
                model=self.config.gemini_model,
                contents=full_prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            return response.text
        else:
            # Old SDK (google.generativeai)
            response = client.generate_content(
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

    # ── Cache Management ─────────────────────────────────────
    def clear_cache(self) -> int:
        """Clear the response cache. Returns number of evicted entries."""
        with self._cache_lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"LLM cache cleared ({count} entries)")
            return count

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
