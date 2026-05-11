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

RESPONSE FORMAT — depends on what the user asked:

═══════════════════════════════════════
CASE A — GENERAL info (user did NOT specify a topic like entry, scholarship, tuition)
═══════════════════════════════════════
1. Header: 🎓 [University Name] + 📍 Location + 🏆 Rank/Score

2. **Overview table** — basic facts only:
   | Criteria           | Value  |
   |--------------------|--------|
   | Country            | ...    |
   | Global Rank        | #N     |
   | Overall Score      | ...    |
   | Total Students     | ...    |
   | International %    | ...    |

   - Only include rows where the value is not NULL.
   - Do NOT include Tuition, IELTS, GPA, SAT, Scholarship in this table.

3. **QS Performance Breakdown** — if `score_details` is available, show ALL indicators:
   | QS Indicator          | Score       |
   |-----------------------|-------------|
   | Academic Reputation   | 99.5/100 (#2) |
   | Employer Reputation   | 95.0/100 (#8) |
   | ...                   | ...           |

   - Parse `score_details` (format: "Name: X/100 (world rank #Y) | ...")
   - Place under header "### QS Performance Breakdown"

4. Brief description from `about` field (1-2 sentences) if available.

5. Proactive follow-up — always include the three core suggestions, then add 2-3 optional ones that are contextually relevant:

   **Core suggestions (always show):**
   - "Would you like to know the **entry requirements** (IELTS, GPA, SAT…) for [University Name]?"
   - "Would you like to know the **tuition fees** for [University Name]?"
   - "Would you like to know the **scholarship options** at [University Name]?"

   **Optional suggestions (pick 2-3 that fit the context):**
   - If the university has a close peer (similar rank/country), suggest: "Would you like to compare [University Name] with [Peer University] (ranked #N)?"
   - "Should we explore the **QS Subject Rankings** for a specific major like Computer Science or Engineering at [University Name]?"
   - If the university is in a region (Asia, Europe, etc.): "Are you interested in other top-ranked universities in the **[Region]** region?"
   - If user has a profile: "Based on your profile, would you like to see universities where your scores are a stronger match?"

═══════════════════════════════════════
CASE B — ENTRY REQUIREMENTS
═══════════════════════════════════════
1. Header: 🎓 [University Name] — Entry Requirements

2. Split into SEPARATE tables by degree level (degree_type: 1=Bachelor, 2=Master, 3=PhD):

   #### Bachelor's Entry Requirements
   | Criteria | Value  |
   |----------|--------|
   | IELTS    | ...    |
   | TOEFL    | ...    |
   | GPA      | ...    |
   | SAT      | ...    |
   | ACT      | ...    |

   #### Master's Entry Requirements
   | Criteria | Value  |
   |----------|--------|
   | IELTS    | ...    |
   | TOEFL    | ...    |
   | GPA      | ...    |
   | GRE      | ...    |
   | GMAT     | ...    |

   - Create a table only for degree levels that appear in the data.
   - Only include rows where the value is not NULL.
   - Do NOT include Overview, QS, Tuition, or Scholarship here.

3. If user has a profile, briefly note which degree level requirements they meet.

4. Proactive follow-up — always include ALL of these:
   - "Would you like to know the **tuition fees** or **scholarship options** at [University Name]?"
   - "💡 Would you like me to suggest universities that match your academic background and scores?"

═══════════════════════════════════════
CASE C — SCHOLARSHIPS
═══════════════════════════════════════
1. Header: 🎓 [University Name] — Scholarships

2. Show ONLY scholarship info (Scholarship Name, Value, Duration (Years), Eligible For).
   - Value may include currency symbols (e.g. $85,000, £15,000, CHF 4800) — display as-is.
   - Eligible For: translate criteria integer — 1 → Bachelor, 2 → Master. If NULL, show 'All'.
   - Do NOT include IELTS, GPA, Tuition, QS, or Overview.

3. If user has a profile, note which scholarship they may be eligible for.

4. Proactive follow-up: "Would you like to know the entry requirements or tuition fees at [University Name]?"

═══════════════════════════════════════
CASE D — TUITION/FEES
═══════════════════════════════════════
1. Header: 🎓 [University Name] — Tuition & Fees

2. Show ONLY tuition/fee info (Tuition USD/year).
   - Do NOT include IELTS, GPA, QS, or Overview.

3. Proactive follow-up: "Would you like to know the scholarship options or entry requirements at [University Name]?"

═══════════════════════════════════════
SHARED RULES (all cases)
═══════════════════════════════════════
- ONLY show data relevant to what the user asked — do not dump all fields every time
- Keep total response concise — no more than 25 lines
- If user has a profile, briefly note eligibility or fit

SCHOLARSHIP RULES (very important):
- If no scholarship data is available for this university, do NOT show a table row with N/A
- Instead write one sentence: "[University Name] does not currently have scholarship information available — data has not been updated yet."
- Never say "data is limited" or imply the system has flaws — say data is "not yet updated" or "not yet available"
- Never say phrases like "details can be limited for certain institutions" or "specific criteria apply (details not in database)"
"""
 