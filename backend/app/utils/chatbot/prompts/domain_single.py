"""
DOMAIN_SINGLE_PROMPT — For queries about a single university.
"""

DOMAIN_SINGLE_PROMPT = """{system_context}

---
TASK: Present information about the requested university.

USER REQUEST: "{message}"

CONVERSATION HISTORY:
{history}

{profile_section}

DATABASE RESULTS:
{formatted_data}

RESPONSE FORMAT:
1. Header: 🎓 [University Name] + 📍 Location + 🏆 Rank/Score
2. Markdown table with ALL available data fields (dynamic columns — omit columns where all values are NULL):
   - Possible columns: Tuition (USD), IELTS, TOEFL, GPA, SAT, GRE, GMAT, Scholarship
   - If entry requirements differ by degree type (Bachelor vs Master), show separate rows
3. QS Highlights: 1 line with top 3 indicator scores (from score_details field) if available
4. Brief description from 'about' field (1-2 sentences) if available
5. Proactive follow-up: 2-3 specific suggestions (compare with X? scholarship details? specific major?)

RULES:
- Present ALL data from the database results — do not skip fields
- If score_details is available, parse and show top 3 indicators
- If user has a profile, briefly note eligibility status
- Keep total response concise — no more than 20 lines
"""
 