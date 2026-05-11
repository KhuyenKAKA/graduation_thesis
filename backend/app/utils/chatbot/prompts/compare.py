"""
COMPARE_PROMPT — For comparing 2+ universities side by side.
"""

COMPARE_PROMPT = """{system_context}

---
TASK: Compare the universities in detail using a transposed comparison matrix.

USER REQUEST: "{message}"

CONVERSATION HISTORY:
{history}

{profile_section}

DATABASE RESULTS:
{formatted_data}

RESPONSE FORMAT — depends on what the user asked:

═══════════════════════════════════════
CASE A — GENERAL comparison (user did NOT specify a topic like entry, scholarship, tuition)
═══════════════════════════════════════
1. Go DIRECTLY to the overview table — no lengthy introduction.

   **Overview:**
   | Criteria           | [University 1] | [University 2] |
   |--------------------|----------------|----------------|
   | Country            | ...            | ...            |
   | Global Rank        | ...            | ...            |
   | Overall Score      | ...            | ...            |
   | Total Students     | ...            | ...            |
   | International %    | ...            | ...            |

   - Only include rows where at least one university has data. NULL → "N/A".
   - Do NOT include entry requirements, tuition, or scholarship in this table.

2. **Table 2 — QS Performance Breakdown** (if `score_details` is available):

   | QS Indicator | [University 1] | [University 2] |
   |---|---|---|
   | Academic Reputation | 99.5/100 (#2) | 98.1/100 (#5) |
   | ... | ... | ... |

   - Parse `score_details` (format: "Name: X/100 (world rank #Y) | ...")
   - Show Score/100 and world rank (#N) in each cell
   - **Bold** the WINNER (higher score) in each row
   - Place under header "### QS Performance Breakdown"

3. Brief assessment (2-3 sentences): overall ranking difference, scale, prestige.

4. **Recommendations:**
   - 🏆 Best overall prestige: [Name] — [reason, e.g. higher rank / QS score]
   - 🌍 Best for international students: [Name] — [reason, e.g. higher international %]
   - If user has a profile: "Based on your profile, [Name] is a better fit because [reason]"

5. Proactive follow-up — ask the user if they want to dive deeper. Always suggest BOTH:
   - "Would you like to compare the **entry requirements** (IELTS, GPA, SAT…) for these universities?"
   - "Would you like to compare **tuition fees and scholarships**?"

═══════════════════════════════════════
CASE B — ENTRY REQUIREMENTS comparison
═══════════════════════════════════════
1. Split into SEPARATE tables by degree level. Do NOT merge Bachelor and Master.
   Produce one table per degree level that has data (degree_type: 1=Bachelor, 2=Master, 3=PhD):

   #### Bachelor's Entry Requirements
   | Criteria | [University 1] | [University 2] |
   |----------|----------------|----------------|
   | IELTS    | ...            | ...            |
   | TOEFL    | ...            | ...            |
   | GPA      | ...            | ...            |
   | SAT      | ...            | N/A            |
   | ACT      | N/A            | ...            |

   #### Master's Entry Requirements
   | Criteria | [University 1] | [University 2] |
   |----------|----------------|----------------|
   | IELTS    | ...            | ...            |
   | TOEFL    | ...            | ...            |
   | GPA      | ...            | ...            |
   | GRE      | ...            | N/A            |
   | GMAT     | N/A            | ...            |

   - Include a row for a criterion if AT LEAST ONE university has a non-NULL value for it at that degree level.
   - NEVER drop a row just because one university has NULL — show "N/A" instead.
   - Do NOT include QS Performance Breakdown or Overview table here.

2. Brief assessment (2-3 sentences): compare selectivity, which is easier/harder to get into.

3. **Recommendations:**
   - ✅ Easier to get into: [Name] — [reason, e.g. lower GPA/IELTS threshold]
   - 🎯 Best for strong applicants: [Name] — [reason]
   - If user has a profile: "Based on your scores, you meet the requirements for [Name] but may need to improve [score] for [Name]"

4. Proactive follow-up: "Would you like to compare tuition fees and scholarships for these universities?"

═══════════════════════════════════════
CASE C — SCHOLARSHIPS comparison
═══════════════════════════════════════
1. Show ONLY scholarship rows (Scholarship Name, Value, Duration, Eligible For).
   - Value may include currency symbols (e.g. $85,000, £15,000, CHF 4800) — display as-is.
   - Duration: show as number of years (e.g. 4 years).
   - Eligible For: translate criteria integer — 1 → Bachelor, 2 → Master. If NULL, show 'All'.
   - Do NOT include IELTS, GPA, Tuition, QS tables, or Overview table.

2. Brief assessment (2 sentences): compare scholarship availability and value where comparable (note different currencies if applicable).

3. **Recommendations:**
   - 💰 Best scholarship value: [Name] — [reason, e.g. higher value or more options]
   - If user has a profile: note which scholarship the user is most likely eligible for (Bachelor/Master)

4. Proactive follow-up: "Would you like to compare entry requirements or tuition fees?"

═══════════════════════════════════════
CASE D — TUITION/FEES comparison
═══════════════════════════════════════
1. Show ONLY fee-related rows (Tuition USD/year, Scholarship if available).
   - Do NOT include IELTS, GPA, QS tables, or Overview table.

2. Brief assessment (2 sentences): which is cheaper, value proposition.

3. **Recommendations:**
   - 💵 Best value for money: [Name] — [reason, e.g. lower tuition with similar rank]
   - 🎓 Best overall considering cost + rank: [Name] — [reason]

4. Proactive follow-up: "Would you like to compare entry requirements or scholarships?"

═══════════════════════════════════════
SHARED RULES (all cases)
═══════════════════════════════════════
- Do NOT write individual university blocks before the table
- Keep column widths consistent
- If user has a profile, briefly note which university is a better fit
- Maximum response: ~50 lines

SCHOLARSHIP RULES (very important):
- If a university has no scholarship data, do NOT show a row with N/A values for it in the table
- Instead, after the table write a short note like: "Note: Harvard University does not currently have scholarship data available in our system."
- Never say "data is limited" or imply the system has flaws — say "data has not been updated yet" or "not yet available"
- Never say phrases like "details can be limited for certain institutions" or "data is not in database"
"""
 