"""
DOMAIN_LISTING_PROMPT — For queries returning multiple universities (top N, search results).
"""

DOMAIN_LISTING_PROMPT = """{system_context}

---
TASK: Present a list of universities matching the user's criteria.

USER REQUEST: "{message}"

CONVERSATION HISTORY:
{history}

{profile_section}

DATABASE RESULTS ({result_count} universities found):
{formatted_data}

RESPONSE FORMAT:
1. Brief summary: "Found X universities matching [criteria]" (1 sentence)
2. Markdown table with dynamic columns:
   - Always: University Name, Rank
   - Conditional (only show if at least one row has non-NULL value):
     Tuition (USD), IELTS, TOEFL, GPA, SAT, Scholarship
   - If a major_name field exists in the data, add a "QS Major" column
   - Show up to 10 rows in the table; if more exist, note "... and X more"
3. Quick insights (2-3 bullet points):
   - Best ranked: [Name] (#rank)
   - Best value: [Name] ($fee/year)
   - If user has profile: "Based on your profile, [Name] and [Name] are best matches"
4. Proactive follow-up: suggest comparing top picks, or viewing details of a specific one

RULES:
- Present data from database results ONLY — never invent universities
- Format numbers: $45,000 (with comma), ranks as #21
- If no results found, say so clearly and suggest adjusting criteria
- Keep the response focused and scannable — no long paragraphs
"""
 