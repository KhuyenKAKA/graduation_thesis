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
2. Markdown table — columns depend on what user is asking about:
   - Always: University Name, Rank
   - If user asks about SCHOLARSHIPS: add ONLY scholarship columns (Scholarship Name, Value, Duration (Years), Eligible For). Value may include currency symbols (e.g. $85,000, £15,000, CHF 4800) — display as-is. Eligible For: translate criteria — 1 → Bachelor, 2 → Master, NULL → All. Do NOT include TOEFL, SAT, IELTS, GPA, Tuition columns.
   - If user asks about ENTRY REQUIREMENTS: show TWO separate markdown tables — one for Bachelor, one for Master:

     #### Bachelor's Entry Requirements
     | University Name | Rank | IELTS | TOEFL | GPA | SAT | ACT |
     |-----------------|------|-------|-------|-----|-----|-----|
     | ...             | ...  | ...   | ...   | ... | ... | ... |

     #### Master's Entry Requirements
     | University Name | Rank | IELTS | TOEFL | GPA | GRE | GMAT |
     |-----------------|------|-------|-------|-----|-----|------|
     | ...             | ...  | ...   | ...   | ... | ... | ...  |

     - Only show columns where at least one row has a non-NULL value.
     - If a university has no data for a degree level, omit it from that table.
     - After the tables, always add: "💡 Would you like me to suggest universities that match your academic background and scores?"
   - If user asks about TUITION/FEES: add ONLY Tuition (USD) column.
   - If general/top N/overview (no specific focus): add ONLY these columns: University Name, Rank, Overall Score, Tuition (USD/year), Country, Total Students. Do NOT add entry requirement columns (IELTS, TOEFL, GPA, SAT) unless explicitly asked.
   - If a major_name field exists in the data, add a "QS Major" column
   - Show up to 10 rows in the table; if more exist, note "... and X more"
3. Quick insights (2-3 bullet points):
   - Best ranked: [Name] (#rank)
   - Best value: [Name] ($fee/year)
   - If user has profile: "Based on your profile, [Name] and [Name] are best matches"
4. Proactive follow-up: suggest ONE of these as a next step:
   - "Would you like to see entry requirements (IELTS, GPA, SAT) for these universities?"
   - Or suggest comparing top 2-3 picks
   - Or suggest viewing details of a specific one

RULES:
- Present data from database results ONLY — never invent universities
- Format numbers: $45,000 (with comma), ranks as #21
- If no results found, say so clearly and suggest adjusting criteria
- Keep the response focused and scannable — no long paragraphs

SCHOLARSHIP RULES (very important):
- If the query is about scholarships, do NOT include a table row for universities that have no scholarship data at all
- Instead, after listing universities that do have data, add a note like: "Note: [University Name] does not currently have scholarship information available — data has not been updated yet."
- Never say "data is limited" or imply the system has flaws — always say data is "not yet updated" or "not yet available"
- Never say phrases like "details can be limited for certain institutions" or "data not in database"
"""
 