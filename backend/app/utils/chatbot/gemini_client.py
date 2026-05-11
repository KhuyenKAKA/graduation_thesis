"""
GeminiClient � Tiered AI API client with automatic fallback.

Endpoint URLs and internal model names are configured via .env � never hardcoded here.
The public-facing model name shown to users is always controlled by PRIMARY_MODEL in .env.
"""

from __future__ import annotations

import time
from typing import Generator, Optional


class GeminiClient:

    _GOOGLE_MODEL_ORDER = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-lite",
    ]

    def __init__(
        self,
        primary_key: str = "",
        primary_base: str = "",
        primary_model: str = "",
        wokushop_key: str = "",
        wokushop_base: str = "",
        wokushop_model: str = "",
        google_key: str = "",
    ):
        self._rate_limited = False


        self._primary_client = None
        self._primary_model = primary_model
        self._primary_ready = False
        if primary_key and primary_base:
            self._init_openai_compat(
                key=primary_key, base=primary_base,
                client_attr="_primary_client", ready_attr="_primary_ready",
                label="primary",
            )

        self._wokushop_client = None
        self._wokushop_model = wokushop_model
        self._wokushop_ready = False
        if wokushop_key and wokushop_base:
            self._init_openai_compat(
                key=wokushop_key, base=wokushop_base,
                client_attr="_wokushop_client", ready_attr="_wokushop_ready",
                label="wokushop",
            )

        self._google_client = None
        self._google_model = self._GOOGLE_MODEL_ORDER[0]
        self._google_ready = False
        if google_key:
            self._init_google(google_key)

    # Properties

    @property
    def is_ready(self) -> bool:
        return self._primary_ready or self._wokushop_ready or self._google_ready

    @property
    def is_rate_limited(self) -> bool:
        return self._rate_limited

    # Initialisation helpers

    def _init_openai_compat(self, key: str, base: str, client_attr: str, ready_attr: str, label: str) -> None:
        try:
            from openai import OpenAI
            setattr(self, client_attr, OpenAI(api_key=key, base_url=base))
            setattr(self, ready_attr, True)
            print(f"[GeminiClient] {label} ready.")
        except Exception as exc:
            print(f"[GeminiClient] {label} init failed: {exc}")
            setattr(self, ready_attr, False)

    def _init_google(self, api_key: str) -> None:
        try:
            from google import genai
            self._google_client = genai.Client(api_key=api_key)
            self._google_ready = True
            print("[GeminiClient] Google genAI ready.")
        except Exception as exc:
            print(f"[GeminiClient] Google genAI init failed: {exc}")
            self._google_ready = False

    # Non-streaming call

    def call(self, prompt: str, temperature: float = 0.2, max_tokens: int = 2048) -> Optional[str]:
        """Sync call. Tries primary -> wokushop -> Google genAI."""
        if self._primary_ready:
            result = self._call_openai_compat(
                self._primary_client, self._primary_model,
                prompt, temperature, max_tokens, "primary",
            )
            if result is not None:
                return result
            print("[GeminiClient] Primary failed, trying wokushop.")

        if self._wokushop_ready:
            result = self._call_openai_compat(
                self._wokushop_client, self._wokushop_model,
                prompt, temperature, max_tokens, "wokushop",
            )
            if result is not None:
                return result
            print("[GeminiClient] Wokushop failed, trying Google genAI.")

        if self._google_ready:
            return self._call_google(prompt, temperature, max_tokens)

        print("[GeminiClient] All tiers exhausted.")
        return None

    def _call_openai_compat(
        self, client, model: str,
        prompt: str, temperature: float, max_tokens: int, label: str,
    ) -> Optional[str]:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            choice = resp.choices[0]
            content = choice.message.content
            if not content:
                print(f"[GeminiClient] {label} returned empty content.")
                return None
            return content
        except Exception as exc:
            print(f"[GeminiClient] {label} error: {exc}")
            return None

    def _call_google(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        from google.genai import types
        start_idx = self._get_google_start_index()
        for model in self._GOOGLE_MODEL_ORDER[start_idx:]:
            for attempt in range(3):
                try:
                    resp = self._google_client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens,
                        ),
                    )
                    self._google_model = model
                    self._rate_limited = False
                    return resp.text
                except Exception as exc:
                    if not self._handle_error(exc, model, attempt):
                        break
        self._rate_limited = True
        print("[GeminiClient] All Google models exhausted.")
        return None

    # Streaming call

    def stream(self, prompt: str, temperature: float = 0.3, max_tokens: int = 3000) -> Generator[str, None, None]:
        """Streaming call. Tries primary -> wokushop -> Google genAI."""
        if self._primary_ready:
            try:
                chunks = list(self._stream_openai_compat(
                    self._primary_client, self._primary_model,
                    prompt, temperature, max_tokens,
                ))
                if chunks:
                    yield from chunks
                    return
            except Exception as exc:
                print(f"[GeminiClient] Primary streaming failed ({exc}), trying wokushop.")

        if self._wokushop_ready:
            try:
                chunks = list(self._stream_openai_compat(
                    self._wokushop_client, self._wokushop_model,
                    prompt, temperature, max_tokens,
                ))
                if chunks:
                    yield from chunks
                    return
            except Exception as exc:
                print(f"[GeminiClient] Wokushop streaming failed ({exc}), trying Google genAI.")

        if self._google_ready:
            yield from self._stream_google(prompt, temperature, max_tokens)
            return

        yield "AI service is not configured. Please set API keys in .env"

    def _stream_openai_compat(
        self, client, model: str,
        prompt: str, temperature: float, max_tokens: int,
    ) -> Generator[str, None, None]:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def _stream_google(self, prompt: str, temperature: float, max_tokens: int) -> Generator[str, None, None]:
        from google.genai import types
        start_idx = self._get_google_start_index()
        for model in self._GOOGLE_MODEL_ORDER[start_idx:]:
            for attempt in range(3):
                try:
                    response_stream = self._google_client.models.generate_content_stream(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens,
                        ),
                    )
                    self._google_model = model
                    self._rate_limited = False
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                    return
                except Exception as exc:
                    if not self._handle_error(exc, model, attempt):
                        break
        self._rate_limited = True
        yield "\n The AI service is temporarily unavailable. Please try again in a few minutes."

    # Helpers

    def _get_google_start_index(self) -> int:
        try:
            return self._GOOGLE_MODEL_ORDER.index(self._google_model)
        except ValueError:
            return 0

    def _handle_error(self, exc: Exception, model: str, attempt: int) -> bool:
        """Returns True to retry same model, False to try next model."""
        exc_str = str(exc)
        if "503" in exc_str or "UNAVAILABLE" in exc_str.upper():
            wait = 2 ** attempt
            print(f"[GeminiClient] 503 on {model} - retry in {wait}s (attempt {attempt + 1}/3)")
            time.sleep(wait)
            return True
        elif "429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str.upper():
            print(f"[GeminiClient] 429 quota on {model} - trying next")
            return False
        else:
            print(f"[GeminiClient] Error on {model}: {exc}")
            return False
