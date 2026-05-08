"""
DOMAIN_PROFILE_PROMPT — For profile-based recommendations (REACH/MATCH/SAFETY).
"""

DOMAIN_PROFILE_PROMPT = """{system_context}

---
TASK: Recommend universities based on the user's academic profile. Classify each into REACH / MATCH / SAFETY.

USER REQUEST: "{message}"

CONVERSATION HISTORY:
{history}

USER PROFILE:
{profile_section}

DATABASE RESULTS:
{formatted_data}

CLASSIFICATION RULES:
- REACH: University requirements EXCEED user's scores (challenging — lower acceptance chance)
- MATCH: University requirements approximately EQUAL user's scores (realistic target)
- SAFETY: University requirements clearly BELOW user's scores (high acceptance probability)

Compare each requirement column (IELTS, TOEFL, GPA, SAT) against the user's profile:
- User score >= requirement → eligible for that criterion
- User score < requirement → below threshold
- Requirement is NULL → cannot assess (note as "unclear")

ENGLISH EXCLUSION:
- If user explicitly states "no English certificate" / "no IELTS":
  - University has IELTS/TOEFL requirement → EXCLUDE ⛔
  - University has NULL IELTS/TOEFL → Flag ⚠️ "requirement unclear"
  - english_test mentions "placement test" or "ESL" → ✅ Include with note

RESPONSE FORMAT:
1. Brief profile summary (1 line): "Based on your profile: IELTS X, GPA X, SAT X..."
2. Markdown table:

| University | Fit Level | Tuition | Key Reason |
|------------|-----------|---------|------------|
| [Name] | REACH | $XX,XXX | IELTS req 7.5 > your 7.0 |
| [Name] | MATCH | $XX,XXX | All requirements met |
| [Name] | SAFETY | $XX,XXX | Requirements below your scores |

3. Application strategy (3-4 lines):
   - REACH (1-2 schools): ambitious targets
   - MATCH (3-4 schools): primary applications
   - SAFETY (1-2 schools): backup options

4. Proactive follow-up: "Want me to compare your top MATCH choices in detail?"

RULES:
- Only recommend universities from the DATABASE RESULTS
- Be honest: if all results are REACH, say so and suggest adjusting criteria
- Never guarantee admission
- Keep response under 25 lines
"""
 