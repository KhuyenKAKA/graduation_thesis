"""
Data quality assessment and formatting utilities.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional, Tuple


# Entry requirement columns to check for data completeness
_REQ_KEYS = ("IELTS", "TOEFL", "GPA", "SAT", "GRE", "GMAT", "ACT")

# Scholarship columns — if any row has these, data is rich enough
_SCHOLARSHIP_KEYS = ("value", "duration", "criteria")

# Generic columns that signal meaningful payload (not just identifiers)
_IDENTIFIER_KEYS = frozenset({"id", "university_id", "country_id", "name", "rank"})


def check_data_quality(db_data: List[Dict]) -> Tuple[bool, str]:
    """
    Assess whether the database results have sufficient data to answer the query.

    Returns:
        (is_data_poor, found_schools_context):
        - is_data_poor: True if data is insufficient
        - found_schools_context: String listing found university names
    """
    if not db_data:
        return True, ""

    names = [r.get("name", "") for r in db_data[:5] if r.get("name")]
    found_schools = f"Universities found: {', '.join(names)}" if names else ""

    top_records = db_data[:10]

    # If ANY row has a non-null entry requirement, data is rich
    has_any_req = any(
        r.get(k) is not None
        for r in top_records
        for k in _REQ_KEYS
    )
    if has_any_req:
        return False, found_schools

    # If ANY row has scholarship data, data is rich
    has_any_scholarship = any(
        r.get(k) is not None
        for r in top_records
        for k in _SCHOLARSHIP_KEYS
    )
    if has_any_scholarship:
        return False, found_schools

    # Generic fallback: if any row has a non-null non-identifier field, data is usable
    has_any_payload = any(
        v is not None
        for r in top_records
        for k, v in r.items()
        if k not in _IDENTIFIER_KEYS
    )
    if has_any_payload:
        return False, found_schools

    # Check fee coverage
    fee_missing_count = sum(1 for r in top_records if r.get("fee") is None)
    is_poor = fee_missing_count >= max(1, len(top_records) // 2)
    return is_poor, found_schools


def format_db_data(data: List[Dict], limit: int = 15) -> str:
    """
    Format DB rows as numbered JSON strings for AI prompt injection.

    Args:
        data: List of database result dictionaries.
        limit: Maximum number of rows to include.

    Returns:
        Formatted string with numbered candidates.
    """
    if not data:
        return "No data available."
    rows = []
    for i, rec in enumerate(data[:limit], 1):
        rows.append(f"Candidate #{i}: {json.dumps(rec, ensure_ascii=False, default=str)}")
    return "\n".join(rows)


def format_history(history: List[Dict], limit: int = 5, summary: str = "") -> str:
    """Format conversation history for prompt injection."""
    lines = []
    if summary:
        lines.append(f"[Earlier conversation summary]: {summary}")
    if not history:
        return "\n".join(lines) if lines else "(No previous conversation)"
    recent = history[-limit:]
    for msg in recent:
        role = "User" if msg.get("role") == "user" else "Assistant"
        lines.append(f"{role}: {msg.get('content', '')[:300]}")
    return "\n".join(lines)


def format_user_profile(profile: Optional[Dict]) -> str:
    """Format user StudyBG into a readable block for AI prompts."""
    if not profile:
        return ""
    fields = [
        ("level", "Level"),
        ("major", "Major"),
        ("gpa", "GPA"),
        ("ielts", "IELTS"),
        ("toefl", "TOEFL"),
        ("sat", "SAT"),
        ("gre", "GRE"),
        ("gmat", "GMAT"),
        ("act", "ACT"),
        ("inter_bac", "IB Score"),
        ("cam_adv_test", "Cambridge Advanced"),
        ("graduate_year", "Graduation Year"),
        ("country", "Country"),
        ("main_lang", "Main Language"),
        ("add_lang", "Second Language"),
    ]
    lines = []
    for key, label in fields:
        val = profile.get(key)
        if val is not None:
            lines.append(f"  {label}: {val}")
    if not lines:
        return ""
    return "USER PROFILE (stored scores):\n" + "\n".join(lines) + "\n"
 