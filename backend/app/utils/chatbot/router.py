"""
IntentRouter — Context-aware intent classification.

Returns (intent, sub_intent) based on the message and conversation history.
Intent: DOMAIN | CHITCHAT
Sub-intent: SINGLE_UNIVERSITY | LISTING | COMPARE | PROFILE_MATCH | FOLLOW_UP | INFO_RETRIEVAL
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple


class IntentRouter:
    """
    Context-aware intent router.
    Uses keyword matching + history context to classify user messages.
    """

    # Keywords that strongly indicate a domain (study abroad) query
    _DOMAIN_KEYWORDS = [
        'university', 'universities', 'college', 'tuition', 'scholarship',
        'requirement', 'admission', 'campus', 'degree',
        'compare', 'major', 'program', 'ranking',
        'study abroad', 'enroll', 'graduate',
        'undergraduate', 'postgraduate', 'master', 'bachelor',
        'eligible', 'certificate',
        'suggest', 'recommend', 'suitable', 'match', 'fit my',
        'my profile', 'my score', 'my gpa', 'my ielts',
        'information', 'info', 'details',
    ]

    # Short keywords that need word-boundary matching to avoid false positives
    _SHORT_KEYWORDS = {
        'gpa', 'ielts', 'toefl', 'gre', 'gmat', 'act',
    }

    # Compound keywords: must appear together (avoid 'sat' alone matching "I sat down")
    _COMPOUND_KEYWORDS = [
        ('sat', r'\b(sat\s+score|sat\s+requirement|sat\s+\d{3,4})\b'),
        ('fee', r'\b(tuition\s+fee|fee\s+per|annual\s+fee)\b'),
    ]

    # Follow-up patterns indicating continuation of previous topic
    _FOLLOW_UP_PATTERNS = [
        r'\bmore\b', r'\bwhat about\b', r'\bhow about\b',
        r'\bthen\b', r'\balso\b', r'\bother\b', r'\band\s+\w+\?',
        r'\btell me more\b', r'\bshow me\b', r'\bany other\b',
        r'\bit\b.*\?$', r'\bthat one\b', r'\bthis one\b',
    ]

    # Compare indicators
    _COMPARE_PATTERNS = [
        r'\bcompare\b', r'\bvs\.?\b', r'\bversus\b',
        r'\bbetween\b', r'\bdifference between\b',
    ]

    # Profile match indicators
    _PROFILE_PATTERNS = [
        r'\bfit my\b', r'\bmy profile\b',
        r'\bsuggest\b.*\bfor me\b',
        r'\bsuitable\b.*\bfor me\b', r'\bsuitable for me\b',
        r'\bmy\b.*\bbackground\b', r'\bmy academic\b',
        r'\bam i eligible\b', r'\bcan i get in\b',
        r'\bno ielts\b', r'\bno english\b',
        r'\blow gpa\b',
        r'\bfor me\b',
    ]

    def classify(self, text: str, history: Optional[List[Dict]] = None) -> Tuple[str, str]:
        """
        Classify user message into (intent, sub_intent).

        Args:
            text: Current user message
            history: Recent conversation history [{"role": "user"|"assistant", "content": "..."}]

        Returns:
            Tuple of (intent, sub_intent):
            - intent: "DOMAIN" or "CHITCHAT"
            - sub_intent: "COMPARE", "PROFILE_MATCH", "SINGLE_UNIVERSITY",
                         "LISTING", "FOLLOW_UP", "INFO_RETRIEVAL", or ""
        """
        tl = text.lower().strip()

        # 1. Check compare patterns first (high priority)
        if self._matches_patterns(tl, self._COMPARE_PATTERNS):
            return ("DOMAIN", "COMPARE")

        # 2. Check profile/eligibility patterns
        if self._matches_patterns(tl, self._PROFILE_PATTERNS):
            return ("DOMAIN", "PROFILE_MATCH")

        # 3. Check explicit domain keywords
        if self._has_domain_keywords(tl):
            sub = self._detect_sub_intent(tl, history)
            return ("DOMAIN", sub)

        # 4. Check follow-up patterns (needs history context)
        if history and self._is_follow_up(tl, history):
            return ("DOMAIN", "FOLLOW_UP")

        # 5. Context carry-over: if recent history was DOMAIN and message is short
        if history and self._should_carry_domain(tl, history):
            return ("DOMAIN", "FOLLOW_UP")

        # 6. Default: CHITCHAT
        return ("CHITCHAT", "")

    def _has_domain_keywords(self, text: str) -> bool:
        """Check if text contains any domain keywords."""
        # Check short keywords with word boundaries
        for kw in self._SHORT_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                return True

        # Check compound keywords
        for _, pattern in self._COMPOUND_KEYWORDS:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        # Check regular keywords
        for kw in self._DOMAIN_KEYWORDS:
            if kw in text:
                return True

        return False

    def _matches_patterns(self, text: str, patterns: list) -> bool:
        """Check if text matches any regex pattern in the list."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _is_follow_up(self, text: str, history: List[Dict]) -> bool:
        """Detect follow-up messages that continue previous topic."""
        if self._matches_patterns(text, self._FOLLOW_UP_PATTERNS):
            return True
        # Questions under 6 words ending with ? after domain messages
        if text.endswith('?') and len(text.split()) <= 6:
            if self._recent_was_domain(history):
                return True
        return False

    def _should_carry_domain(self, text: str, history: List[Dict]) -> bool:
        """
        If recent conversation was about universities (DOMAIN) and current message
        is short/ambiguous, keep it as DOMAIN to maintain context.
        """
        if len(text.split()) > 8:
            return False
        return self._recent_was_domain(history)

    def _recent_was_domain(self, history: List[Dict]) -> bool:
        """Check if recent messages indicate domain conversation."""
        if not history:
            return False
        # Check last 3 messages for domain indicators
        recent = history[-3:]
        domain_indicators = [
            'university', 'rank', 'tuition', 'ielts',
            'scholarship', 'gpa',
        ]
        for msg in recent:
            content = (msg.get("content") or "").lower()[:200]
            for indicator in domain_indicators:
                if indicator in content:
                    return True
        return False

    def _detect_sub_intent(self, text: str, history: Optional[List[Dict]]) -> str:
        """Detect sub-intent for domain queries."""
        # Count university name mentions (heuristic: capitalized multi-word sequences)
        # If message seems to name exactly 1 university → SINGLE_UNIVERSITY
        # If "top N" or listing request → LISTING
        if re.search(r'\btop\s+\d+\b', text, re.IGNORECASE):
            return "LISTING"
        if re.search(r'\b(cheapest|most expensive|best|most)\b', text, re.IGNORECASE):
            return "LISTING"
        # If the query targets a specific named university
        if self._targets_single_university(text):
            return "SINGLE_UNIVERSITY"
        return "INFO_RETRIEVAL"

    def _targets_single_university(self, text: str) -> bool:
        """Heuristic: does the query ask about a single specific university?"""
        patterns = [
            r'\b(tell me about|info about|information about|information of|details about|give me information)\b',
            r'\b(MIT|Harvard|Stanford|Oxford|Cambridge|Caltech|Yale|Princeton)\b',
            r'\b(what is|what are).*requirement',
            r'\bhow much\b.*\b(tuition|fee)\b',
        ]
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                return True
        return False
 