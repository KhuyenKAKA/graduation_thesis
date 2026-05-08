"""
ChatbotEngine — Main orchestrator for the study abroad advisory chatbot.

Architecture:
  1. IntentRouter      — context-aware classification (DOMAIN/CHITCHAT + sub-intent)
  2. TextToSQLEngine   — Gemini generates MySQL SQL from natural language
  3. SQL Guard         — validates generated SQL for safety
  4. execute_query     — safe MySQL execution
  5. Data Quality      — assess if results are sufficient
  6. Adaptive Prompts  — select prompt based on sub-intent
  7. GeminiClient      — stream or call Gemini for response generation
"""

from __future__ import annotations

from typing import Dict, Generator, List, Optional

from app.database import execute_query
from app.utils.chatbot.gemini_client import GeminiClient
from app.utils.chatbot.router import IntentRouter
from app.utils.chatbot.text_to_sql import TextToSQLEngine
from app.utils.chatbot.sql_guard import validate_sql, SQLValidationError
from app.utils.chatbot.data_quality import (
    check_data_quality,
    format_db_data,
    format_history,
    format_user_profile,
)
from app.utils.chatbot.prompts import (
    SYSTEM_CONTEXT,
    CHITCHAT_PROMPT,
    DOMAIN_SINGLE_PROMPT,
    DOMAIN_LISTING_PROMPT,
    DOMAIN_PROFILE_PROMPT,
    DOMAIN_POOR_PROMPT,
    COMPARE_PROMPT,
)


class ChatbotEngine:
    """
    Study abroad advisory chatbot engine.

    Public methods:
      process(message, history, ...)       -> str          (sync, full response)
      process_stream(message, history, ...) -> Generator   (SSE chunks)
    """

    def __init__(self, gemini_key: Optional[str] = None, tavily_key: Optional[str] = None, gemini_key_pro: Optional[str] = None):
        self._gemini = GeminiClient(gemini_key or "", pro_key=gemini_key_pro or "")
        self._tavily_key = tavily_key
        self._router = IntentRouter()
        self._sql_engine: Optional[TextToSQLEngine] = None

        if self._gemini.is_ready:
            self._sql_engine = TextToSQLEngine(self._gemini.call)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(
        self,
        message: str,
        history: List[Dict],
        user_profile: Optional[Dict] = None,
        history_summary: str = "",
    ) -> str:
        """Sync entry point — returns full response string."""
        intent, sub_intent = self._router.classify(message, history)
        print(f"[Chatbot] intent={intent}/{sub_intent} | msg={message[:60]!r}")

        if intent == "CHITCHAT":
            return self._handle_chitchat(message, history, user_profile, history_summary)
        return self._handle_domain_sync(message, history, user_profile, history_summary, sub_intent)

    def process_stream(
        self,
        message: str,
        history: List[Dict],
        user_profile: Optional[Dict] = None,
        history_summary: str = "",
    ) -> Generator[str, None, None]:
        """
        Streaming entry point — yields text chunks.
        May yield a final special signal: <<ONLINE_SEARCH|{query}>>
        """
        intent, sub_intent = self._router.classify(message, history)
        print(f"[Chatbot] intent={intent}/{sub_intent} | msg={message[:60]!r}")

        if intent == "CHITCHAT":
            yield from self._stream_chitchat(message, history, user_profile, history_summary)
        else:
            yield from self._stream_domain(message, history, user_profile, history_summary, sub_intent)

    # ------------------------------------------------------------------
    # History summarization (called externally by router)
    # ------------------------------------------------------------------

    def summarize_history(self, history: List[Dict]) -> str:
        """Compress older chat messages into a brief summary."""
        if not history or not self._gemini.is_ready:
            return ""
        lines = []
        for msg in history:
            role = "User" if msg.get("role") == "user" else "Assistant"
            lines.append(f"{role}: {msg.get('content', '')[:300]}")
        history_text = "\n".join(lines)
        prompt = (
            "Summarize this study-abroad advisory conversation in 3-5 concise sentences. "
            "Focus on: universities/countries discussed, user scores/profile, "
            "key requirements, and conclusions reached.\n\n"
            f"CONVERSATION:\n{history_text}\n\n"
            "SUMMARY (same language as the conversation):"
        )
        result = self._gemini.call(prompt)
        return result.strip() if result else ""

    # ------------------------------------------------------------------
    # CHITCHAT handling
    # ------------------------------------------------------------------

    def _handle_chitchat(self, message: str, history: List[Dict], profile: Optional[Dict], summary: str) -> str:
        prompt = self._build_chitchat_prompt(message, history, profile, summary)
        reply = self._gemini.call(prompt)
        if reply:
            return reply.strip()
        return self._fallback_greeting()

    def _stream_chitchat(self, message: str, history: List[Dict], profile: Optional[Dict], summary: str) -> Generator[str, None, None]:
        prompt = self._build_chitchat_prompt(message, history, profile, summary)
        yield from self._gemini.stream(prompt)

    def _build_chitchat_prompt(self, message: str, history: List[Dict], profile: Optional[Dict], summary: str) -> str:
        return CHITCHAT_PROMPT.format(
            system_context=SYSTEM_CONTEXT,
            history=format_history(history, limit=5, summary=summary),
            message=message,
            profile_section=format_user_profile(profile),
        )

    # ------------------------------------------------------------------
    # DOMAIN handling — sync
    # ------------------------------------------------------------------

    def _handle_domain_sync(self, message: str, history: List[Dict], profile: Optional[Dict], summary: str, sub_intent: str) -> str:
        if not self._sql_engine:
            return "⚠️ Gemini API is not configured. Please set GEMINI_KEY in .env"

        # Generate SQL
        ok, sql, clarification = self._sql_engine.generate(message, history, profile, history_summary=summary)

        # If clarification needed, return it directly
        if clarification:
            return clarification

        if not ok or not sql:
            if self._gemini.is_rate_limited:
                return "⚠️ AI service is experiencing high demand. Please try again in a few minutes."
            return "Sorry, I couldn't process that question. Try rephrasing or being more specific."

        # Validate SQL
        try:
            sql = validate_sql(sql)
        except SQLValidationError as e:
            print(f"[Chatbot] SQL validation failed: {e}")
            return "Sorry, I couldn't generate a valid query. Please try rephrasing your question."

        # Execute SQL
        try:
            db_data = execute_query(sql, fetch=True) or []
        except Exception as exc:
            print(f"[Chatbot DB] Query error: {exc}")
            db_data = []

        # Check data quality
        is_poor, found_schools = check_data_quality(db_data)

        if is_poor:
            prompt = self._build_poor_prompt(message, history, found_schools, summary)
            reply = self._gemini.call(prompt) or ""
            return reply.strip() + f"\n\n<<ONLINE_SEARCH|{message}>>"

        # Build and execute response prompt
        prompt = self._build_domain_prompt(message, history, profile, summary, sub_intent, db_data)
        reply = self._gemini.call(prompt, max_tokens=3000)
        return reply.strip() if reply else self._plain_fallback(db_data)

    # ------------------------------------------------------------------
    # DOMAIN handling — streaming
    # ------------------------------------------------------------------

    def _stream_domain(self, message: str, history: List[Dict], profile: Optional[Dict], summary: str, sub_intent: str) -> Generator[str, None, None]:
        if not self._sql_engine:
            yield "⚠️ Gemini API is not configured. Please set GEMINI_KEY in .env"
            return

        # Generate SQL
        ok, sql, clarification = self._sql_engine.generate(message, history, profile, history_summary=summary)

        if clarification:
            yield clarification
            return

        if not ok or not sql:
            if self._gemini.is_rate_limited:
                yield "⚠️ AI service is experiencing high demand. Please try again in a few minutes."
            else:
                yield "Sorry, I couldn't process that question. Try rephrasing or being more specific."
            return

        # Validate SQL
        try:
            sql = validate_sql(sql)
        except SQLValidationError as e:
            print(f"[Chatbot] SQL validation failed: {e}")
            yield "Sorry, I couldn't generate a valid query. Please try rephrasing your question."
            return

        # Execute SQL
        try:
            db_data = execute_query(sql, fetch=True) or []
            print(f"[Chatbot SQL] Executed. Found {len(db_data)} rows.")
        except Exception as exc:
            print(f"[Chatbot DB] Query error: {exc}")
            db_data = []

        # Check data quality
        is_poor, found_schools = check_data_quality(db_data)

        if is_poor:
            prompt = self._build_poor_prompt(message, history, found_schools, summary)
            yield from self._gemini.stream(prompt)
            yield f"\n\n<<ONLINE_SEARCH|{message}>>"
            return

        # Build response prompt based on sub-intent
        prompt = self._build_domain_prompt(message, history, profile, summary, sub_intent, db_data)
        yield from self._gemini.stream(prompt)

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------

    def _build_domain_prompt(self, message: str, history: List[Dict], profile: Optional[Dict], summary: str, sub_intent: str, db_data: List[Dict]) -> str:
        """Select and build the appropriate prompt based on sub-intent."""
        formatted_data = format_db_data(db_data)
        history_str = format_history(history, limit=5, summary=summary)
        profile_section = format_user_profile(profile)

        # Choose prompt template based on sub-intent
        if sub_intent == "COMPARE":
            template = COMPARE_PROMPT
        elif sub_intent == "PROFILE_MATCH" and profile:
            template = DOMAIN_PROFILE_PROMPT
        elif sub_intent == "SINGLE_UNIVERSITY" or len(db_data) <= 2:
            template = DOMAIN_SINGLE_PROMPT
        else:
            template = DOMAIN_LISTING_PROMPT

        # Build kwargs for formatting
        kwargs = {
            "system_context": SYSTEM_CONTEXT,
            "message": message,
            "history": history_str,
            "profile_section": profile_section,
            "formatted_data": formatted_data,
        }

        # DOMAIN_LISTING has result_count
        if template == DOMAIN_LISTING_PROMPT:
            kwargs["result_count"] = len(db_data)

        return template.format(**kwargs)

    def _build_poor_prompt(self, message: str, history: List[Dict], found_schools: str, summary: str) -> str:
        return DOMAIN_POOR_PROMPT.format(
            system_context=SYSTEM_CONTEXT,
            message=message,
            history=format_history(history, limit=3, summary=summary),
            found_schools=found_schools or "No universities found in the database.",
        )

    # ------------------------------------------------------------------
    # Fallbacks
    # ------------------------------------------------------------------

    @staticmethod
    def _fallback_greeting() -> str:
        return (
            "Hello! I'm UniAdvisor, your study abroad consultant. I can help you with:\n"
            "- Finding universities by country, ranking, or tuition\n"
            "- Comparing universities side by side\n"
            "- Entry requirements (IELTS, GPA, SAT...)\n"
            "- Scholarship search\n"
            "- Personalized REACH/MATCH/SAFETY recommendations\n\n"
            "What would you like to explore?"
        )

    @staticmethod
    def _plain_fallback(data: List[Dict]) -> str:
        if not data:
            return (
                "No universities found matching your criteria.\n\n"
                "Suggestions:\n"
                "1. Broaden your search (try additional countries or regions)\n"
                "2. Adjust the tuition range or requirements\n"
                "3. Search by region: Asia, Europe, North America...\n\n"
                "Would you like to try a different search?"
            )
        lines = [f"Found {len(data)} result(s):\n"]
        for i, row in enumerate(data[:10], 1):
            name = row.get("name", "Unknown")
            rank = row.get("rank_int") or "N/A"
            country = row.get("country_name") or "N/A"
            fee = row.get("fee")
            fee_str = f"${fee:,.0f}/year" if fee else "N/A"
            lines.append(f"{i}. {name} — Rank #{rank} | {country} | {fee_str}")
        return "\n".join(lines)
 