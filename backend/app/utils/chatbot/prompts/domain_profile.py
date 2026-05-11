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

═══════════════════════════════════════
DEGREE LEVEL TARGETING
═══════════════════════════════════════
Determine the degree level to recommend based on the user's highest completed degree:
- If highest degree = High School / None → recommend Bachelor programs (degree_type = 1)
- If highest degree = Bachelor → recommend Master programs (degree_type = 2)
- If highest degree = Master → recommend PhD programs (degree_type = 3)
- If user explicitly states a target degree level → use that instead

When presenting entry requirements, only show the rows relevant to the targeted degree level (e.g. if recommending Master, show GRE/GMAT/GPA for Master — not SAT for Bachelor).

═══════════════════════════════════════
PRIORITIZATION (ordering within each fit tier)
═══════════════════════════════════════
Within each fit tier (REACH / MATCH / SAFETY), rank universities by the following priority:

1. **Geographic proximity** — prefer countries in the same region as the user's home country.
   - Use the country field in the user profile to infer region (e.g. Vietnam → Southeast Asia/Asia).
   - Universities in the same region rank higher within a tier.

2. **Language compatibility** — prefer universities where the teaching language matches the user's main language or second language.
   - If user's main language = English, English-medium universities are top priority.
   - If user has a second language (e.g. French, German, Japanese), universities in countries where that language is official or commonly used get a boost.
   - Explicitly note language compatibility in the Key Reason column.

3. Rank / score (higher rank = better, as tiebreaker).

═══════════════════════════════════════
SECOND LANGUAGE UNIVERSITIES (MANDATORY when user has add_lang)
═══════════════════════════════════════
If the user profile contains a Second Language (add_lang):
- After the main table, add a **separate section** titled: "🌐 Also Consider — [Second Language] Medium Universities"
- In this section, list 2-3 universities from the DATABASE RESULTS where the country's primary/official language matches the user's second language.
- Apply the same REACH/MATCH/SAFETY classification for these entries.
- In Key Reason, highlight: "[Language] medium · [fit reason]"
- If there are no results in the database for that language, note: "No [language]-medium universities found in current results — try expanding filters."

═══════════════════════════════════════
CLASSIFICATION RULES
═══════════════════════════════════════
- REACH: University requirements EXCEED user's scores (challenging — lower acceptance chance)
- MATCH: University requirements approximately EQUAL user's scores (realistic target)
- SAFETY: University requirements clearly BELOW user's scores (high acceptance probability)

Compare requirement columns relevant to the targeted degree level against the user's profile:
- User score >= requirement → eligible for that criterion
- User score < requirement → below threshold
- Requirement is NULL → cannot assess (note as "unclear")

ENGLISH EXCLUSION:
- If user explicitly states "no English certificate" / "no IELTS":
  - University has IELTS/TOEFL requirement → EXCLUDE ⛔
  - University has NULL IELTS/TOEFL → Flag ⚠️ "requirement unclear"
  - english_test mentions "placement test" or "ESL" → ✅ Include with note

═══════════════════════════════════════
RESPONSE FORMAT
═══════════════════════════════════════
1. Brief profile summary (1 line): "Based on your profile: [degree level targeting, IELTS X, GPA X, country, languages…]"

2. Markdown table — sorted by Fit Level (REACH → MATCH → SAFETY), then by priority rules above:

| University | Country | Fit Level | Tuition | Key Reason |
|------------|---------|-----------|---------|------------|
| [Name] | 🇺🇸 USA |  REACH | $XX,XXX | GPA req 3.8 > your 3.5 |
| [Name] | 🇬🇧 UK  |  MATCH | $XX,XXX | All requirements met · English  |
| [Name] | 🇯🇵 Japan |  SAFETY | $XX,XXX | Requirements below your scores · Japanese  |

   - Use  REACH /  MATCH /  SAFETY for visual clarity
   - In Key Reason: note language match (e.g. "English ", "French ") and proximity (e.g. "Same region ✅") when applicable

3. **If user has a second language**: add a separate section "🌐 Also Consider — [Second Language] Medium Universities" with 2-3 entries using the same table format.

4. Application strategy (3-4 lines):
   - REACH (1-2 schools): ambitious targets
   - MATCH (3-4 schools): primary applications
   - SAFETY (1-2 schools): backup options

5. Proactive follow-up: "Want me to compare your top MATCH choices in detail?"

═══════════════════════════════════════
RULES
═══════════════════════════════════════
- Only recommend universities from the DATABASE RESULTS
- Be honest: if all results are REACH, say so and suggest adjusting criteria
- Never guarantee admission
- Keep response under 30 lines
"""
 