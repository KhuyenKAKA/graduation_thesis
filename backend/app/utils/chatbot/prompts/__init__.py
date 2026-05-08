"""
Prompts package — re-exports all prompt constants.
"""

from app.utils.chatbot.prompts.system_context import SYSTEM_CONTEXT
from app.utils.chatbot.prompts.schema import SCHEMA_CONTEXT
from app.utils.chatbot.prompts.sql_rules import SQL_RULES, SQL_EXAMPLES
from app.utils.chatbot.prompts.chitchat import CHITCHAT_PROMPT
from app.utils.chatbot.prompts.domain_single import DOMAIN_SINGLE_PROMPT
from app.utils.chatbot.prompts.domain_listing import DOMAIN_LISTING_PROMPT
from app.utils.chatbot.prompts.domain_profile import DOMAIN_PROFILE_PROMPT
from app.utils.chatbot.prompts.domain_poor import DOMAIN_POOR_PROMPT
from app.utils.chatbot.prompts.compare import COMPARE_PROMPT

__all__ = [
    "SYSTEM_CONTEXT",
    "SCHEMA_CONTEXT",
    "SQL_RULES",
    "SQL_EXAMPLES",
    "CHITCHAT_PROMPT",
    "DOMAIN_SINGLE_PROMPT",
    "DOMAIN_LISTING_PROMPT",
    "DOMAIN_PROFILE_PROMPT",
    "DOMAIN_POOR_PROMPT",
    "COMPARE_PROMPT",
]
 