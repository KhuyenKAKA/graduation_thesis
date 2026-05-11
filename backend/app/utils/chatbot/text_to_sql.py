"""
TextToSQLEngine — Generates MySQL queries from natural language using Gemini.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Tuple

from app.utils.chatbot.prompts import SCHEMA_CONTEXT, SQL_RULES, SQL_EXAMPLES, SYSTEM_CONTEXT


class TextToSQLEngine:
    """
    Converts natural language questions to MySQL queries.
    Uses conversation history for entity tracking and context resolution.
    """

    def __init__(self, gemini_call):
        """
        Args:
            gemini_call: Callable that takes a prompt string and returns response text.
                         Should be GeminiClient.call method.
        """
        self._call = gemini_call

    def generate(
        self,
        question: str,
        history: List[Dict],
        user_profile: Optional[Dict] = None,
        history_summary: str = "",
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Generate SQL from a natural language question.

        Returns:
            Tuple of (success, sql, clarification):
            - success: True if SQL was generated
            - sql: The generated SQL string (empty if needs_clarification)
            - clarification: Clarification message if question is too vague (None otherwise)
        """
        # Build context from history
        history_str = self._format_history(history, history_summary)
        entity_context = self._extract_entity_context(history)
        profile_hint = self._format_profile_hint(user_profile)

        prompt = self._build_prompt(question, history_str, entity_context, profile_hint)

        print(f"[SQL-Gen] prompt_len={len(prompt)} chars (~{len(prompt)//4} tokens)")
        raw = self._call(prompt, max_tokens=8192)
        if not raw:
            print("[SQL-Gen] ERROR: Gemini returned None/empty")
            return False, "", None

        return self._parse_response(raw)

    def _build_prompt(self, question: str, history_str: str, entity_context: str, profile_hint: str) -> str:
        parts = [
            "You are a MySQL query generator for a university study-abroad advisory system.",
            "Generate ONLY valid JSON output.",
            "",
            SCHEMA_CONTEXT,
            SQL_RULES,
            SQL_EXAMPLES,
        ]
        if profile_hint:
            parts.append(profile_hint)
        if entity_context:
            parts.append(f"\nCURRENT CONTEXT (resolved from conversation):\n{entity_context}")
        parts.append(f"\nCONVERSATION HISTORY:\n{history_str}")
        parts.append(f'\nCURRENT QUESTION: "{question}"')
        parts.append("\nReturn ONLY valid JSON, NO markdown fences:")
        return "\n".join(parts)

    def _format_history(self, history: List[Dict], summary: str = "") -> str:
        """Format conversation history for the SQL prompt."""
        lines = []
        if summary:
            lines.append(f"[Earlier conversation summary]: {summary}")
        limit = 5 if summary else 10
        for msg in history[-limit:]:
            role = "User" if msg.get("role") == "user" else "AI"
            lines.append(f"{role}: {msg.get('content', '')[:200]}")
        return "\n".join(lines) if lines else "(No previous conversation)"

    def _extract_entity_context(self, history: List[Dict]) -> str:
        """
        Extract recently mentioned entities (university names, countries) from history.
        Helps LLM resolve pronouns and follow-up references.
        """
        if not history:
            return ""

        # Scan recent messages for entity mentions
        universities = []
        countries = []

        # Common university names to detect
        uni_patterns = [
            r'\b(MIT|Harvard|Stanford|Oxford|Cambridge|Caltech|Yale|Princeton)\b',
            r'\b(University of \w+)\b',
            r'\b(\w+ University)\b',
        ]
        # Common country names
        country_patterns = [
            r'\b(United States|US|USA|UK|United Kingdom|Canada|Australia|Germany|France|Japan|Korea|Singapore)\b',
        ]

        recent = history[-5:]
        for msg in recent:
            content = msg.get("content", "")[:300]
            for pattern in uni_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                universities.extend(matches)
            for pattern in country_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                countries.extend(matches)

        # Deduplicate and limit
        universities = list(dict.fromkeys(universities))[:3]
        countries = list(dict.fromkeys(countries))[:2]

        parts = []
        if universities:
            parts.append(f"FOCUS universities: {', '.join(universities)}")
        if countries:
            parts.append(f"FOCUS country/region: {', '.join(countries)}")

        return "\n".join(parts)

    def _format_profile_hint(self, profile: Optional[Dict]) -> str:
        """Format user profile as a hint for the SQL generator."""
        if not profile:
            return ""
        parts = []
        for col in ("ielts", "toefl", "gpa", "sat", "gre", "gmat", "act"):
            val = profile.get(col)
            if val is not None:
                parts.append(f"{col.upper()}={val}")
        lang_parts = []
        if profile.get("main_lang"):
            lang_parts.append(f"main_lang={profile['main_lang']}")
        if profile.get("add_lang"):
            lang_parts.append(f"second_lang={profile['add_lang']}")
        result = ""
        if profile.get("country"):
            result += f"\nUSER COUNTRY: {profile['country']}"
        if parts:
            result += f"\nUSER PROFILE: {', '.join(parts)}"
        if lang_parts:
            result += f"\nUSER LANGUAGES: {', '.join(lang_parts)}"
            if profile.get("add_lang"):
                result += (
                    f"\nNOTE: User speaks {profile['add_lang']} as a second language. "
                    "Include universities from countries where this language is official or widely used."
                )
        return result

    def _parse_response(self, raw: str) -> Tuple[bool, str, Optional[str]]:
        """Parse LLM response to extract SQL or clarification."""
        raw = re.sub(r"```(?:json|sql)?\s*|\s*```", "", raw).strip()
        print(f"[SQL-Gen] raw_response={raw[:300]!r}")

        try:
            data = json.loads(raw)

            # Check if clarification is needed
            if data.get("needs_clarification"):
                suggestion = data.get("suggestion", "Could you be more specific?")
                print(f"[SQL-Gen] Needs clarification: {suggestion}")
                return False, "", suggestion

            sql = data.get("sql", "").strip()
            if sql:
                print(f"[SQL-Gen] OK sql={sql[:120]!r}")
                return True, sql, None
            print(f"[SQL-Gen] WARN: JSON parsed but 'sql' key empty. keys={list(data.keys())}")
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"[SQL-Gen] JSON parse error: {e!r} — trying regex fallback")
            m = re.search(r'"sql"\s*:\s*"(.*?)"(?:\s*,|\s*})', raw, re.DOTALL)
            if m:
                sql_extracted = m.group(1).replace('\\"', '"')
                print(f"[SQL-Gen] Regex OK sql={sql_extracted[:120]!r}")
                return True, sql_extracted, None

        print("[SQL-Gen] FAILED: could not extract SQL from response")
        return False, "", None

    def regenerate(
        self,
        question: str,
        history: List[Dict],
        failed_sql: str,
        error_msg: str,
        user_profile: Optional[Dict] = None,
        history_summary: str = "",
    ) -> Tuple[bool, str, Optional[str]]:
        """Retry SQL generation after a DB error, feeding the error back to the LLM."""
        history_str = self._format_history(history, history_summary)
        entity_context = self._extract_entity_context(history)
        profile_hint = self._format_profile_hint(user_profile)

        base_prompt = self._build_prompt(question, history_str, entity_context, profile_hint)
        retry_prompt = (
            f"{base_prompt}\n\n"
            f"PREVIOUS ATTEMPT FAILED:\nSQL: {failed_sql}\n"
            f"ERROR: {error_msg}\n\n"
            "Fix the SQL and return valid JSON again."
        )
        print(f"[SQL-Gen] regenerate prompt_len={len(retry_prompt)}")
        raw = self._call(retry_prompt, max_tokens=4096)
        if not raw:
            return False, "", None
        return self._parse_response(raw)
 