"""
GeminiClient — Handles all Gemini API calls with retry and model fallback.

Call order:
  1. PRIMARY  — gemini-3-flash-preview via wokushop (GEMINI_KEY_PRO)
  2. FALLBACK — Google API key (gemini-2.5-flash → 2.0-flash → 2.0-flash-lite)
"""

from __future__ import annotations

import time
from typing import Generator, Optional

_WOKUSHOP_BASE_URL = "https://llm.wokushop.com/v1"
_PRO_MODEL = "gemini-2.5-flash"


class GeminiClient:
    """Gemini API client with retry, model fallback, and pro endpoint fallback."""

    MODEL_FALLBACK_ORDER = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-lite",
    ]

    def __init__(self, api_key: str, pro_key: str = ""):
        self._client = None
        self._model_name: Optional[str] = None
        self._ready = False
        self._rate_limited = False

        # OpenAI-compatible pro client (wokushop)
        self._pro_client = None
        self._pro_ready = False
        if pro_key:
            self._init_pro(pro_key)

        if api_key:
            self._init(api_key)

    @property
    def is_ready(self) -> bool:
        return self._ready or self._pro_ready

    @property
    def is_rate_limited(self) -> bool:
        return self._rate_limited

    def _init_pro(self, pro_key: str) -> None:
        try:
            from openai import OpenAI
            self._pro_client = OpenAI(api_key=pro_key, base_url=_WOKUSHOP_BASE_URL)
            self._pro_ready = True
            print(f"[GeminiClient] Pro primary ready (model={_PRO_MODEL}, endpoint=wokushop).")
        except Exception as exc:
            print(f"[GeminiClient] Pro init failed: {exc}")
            self._pro_ready = False

    def _init(self, api_key: str) -> None:
        try:
            from google import genai
            self._client = genai.Client(api_key=api_key)
            self._model_name = self.MODEL_FALLBACK_ORDER[0]
            self._ready = True
            print(f"[GeminiClient] Ready (model={self._model_name}).")
        except Exception as exc:
            print(f"[GeminiClient] Init failed: {exc}")
            self._ready = False

    def call(self, prompt: str, temperature: float = 0.2, max_tokens: int = 2048) -> Optional[str]:
        """
        Non-streaming call. Tries pro (wokushop) first, then Google API fallback.
        """
        # 1. PRIMARY: wokushop pro key
        if self._pro_ready:
            result = self._call_pro(prompt, temperature, max_tokens)
            if result is not None:
                return result
            print("[GeminiClient] Pro failed, switching to Google API fallback.")

        # 2. FALLBACK: Google API
        if not self._ready:
            return None
        from google.genai import types

        start_idx = self._get_start_index()

        for model in self.MODEL_FALLBACK_ORDER[start_idx:]:
            for attempt in range(3):
                try:
                    resp = self._client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens,
                        ),
                    )
                    self._on_success(model)
                    return resp.text
                except Exception as exc:
                    if not self._handle_error(exc, model, attempt):
                        break  # try next model

        self._rate_limited = True
        print("[GeminiClient] All models exhausted (quota or error).")
        return None

    def _call_pro(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Non-streaming call via wokushop OpenAI-compatible endpoint."""
        try:
            print(f"[GeminiClient] Calling pro endpoint (model={_PRO_MODEL}).")
            resp = self._pro_client.chat.completions.create(
                model=_PRO_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            choice = resp.choices[0]
            content = choice.message.content
            if not content:
                finish_reason = getattr(choice, "finish_reason", "unknown")
                print(f"[GeminiClient] Pro returned empty content (finish_reason={finish_reason}).")
                return None
            return content
        except Exception as exc:
            print(f"[GeminiClient] Pro endpoint error: {exc}")
            return None

    def stream(self, prompt: str, temperature: float = 0.3, max_tokens: int = 3000) -> Generator[str, None, None]:
        """
        Streaming call. Tries pro (wokushop) first, then Google API fallback.
        """
        # 1. PRIMARY: wokushop pro key
        if self._pro_ready:
            try:
                chunks = list(self._stream_pro(prompt, temperature, max_tokens))
                if chunks:
                    yield from chunks
                    return
            except Exception as exc:
                print(f"[GeminiClient] Pro streaming failed ({exc}), switching to Google API fallback.")

        # 2. FALLBACK: Google API
        if not self._ready:
            yield "⚠️ Gemini API is not configured. Please set GEMINI_KEY or GEMINI_KEY_PRO in .env"
            return
        from google.genai import types

        start_idx = self._get_start_index()

        for model in self.MODEL_FALLBACK_ORDER[start_idx:]:
            for attempt in range(3):
                try:
                    response_stream = self._client.models.generate_content_stream(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens,
                        ),
                    )
                    self._on_success(model)
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                    return  # success
                except Exception as exc:
                    if not self._handle_error(exc, model, attempt):
                        break  # try next model

        self._rate_limited = True
        print("[GeminiClient] All models exhausted (quota or error).")
        yield "\n⚠️ The AI service is temporarily unavailable. Please try again in a few minutes."

    def _stream_pro(self, prompt: str, temperature: float, max_tokens: int) -> Generator[str, None, None]:
        """Streaming call via wokushop OpenAI-compatible endpoint."""
        try:
            print(f"[GeminiClient] Calling pro endpoint streaming (model={_PRO_MODEL}).")
            stream = self._pro_client.chat.completions.create(
                model=_PRO_MODEL,
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
        except Exception as exc:
            print(f"[GeminiClient] Pro endpoint streaming error: {exc}")
            raise

    def _get_start_index(self) -> int:
        try:
            return self.MODEL_FALLBACK_ORDER.index(self._model_name)
        except ValueError:
            return 0

    def _on_success(self, model: str) -> None:
        if model != self._model_name:
            print(f"[GeminiClient] Switched to fallback model: {model}")
            self._model_name = model
        self._rate_limited = False

    def _handle_error(self, exc: Exception, model: str, attempt: int) -> bool:
        """
        Handle API errors. Returns True if should retry same model, False to try next.
        """
        exc_str = str(exc)
        if '503' in exc_str or 'UNAVAILABLE' in exc_str.upper():
            wait = 2 ** attempt
            print(f"[GeminiClient] 503 on {model} — retry in {wait}s (attempt {attempt + 1}/3)")
            time.sleep(wait)
            return True  # retry same model
        elif '429' in exc_str or 'RESOURCE_EXHAUSTED' in exc_str.upper():
            print(f"[GeminiClient] 429 quota exceeded on {model} — trying next model")
            return False  # try next model
        else:
            print(f"[GeminiClient] Error on {model}: {exc}")
            return False  # try next model
 