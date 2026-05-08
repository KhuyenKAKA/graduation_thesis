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

RESPONSE FORMAT:
1. Go DIRECTLY to the comparison table — no lengthy introduction.
2. Use a TRANSPOSED Markdown table (universities as columns, criteria as rows):

| Criteria | [University 1] | [University 2] |
|----------|----------------|----------------|
| Country | ... | ... |
| Global Rank | ... | ... |
| Overall Score | ... | ... |
| Tuition (USD/year) | ... | ... |
| IELTS | ... | ... |
| TOEFL | ... | ... |
| GPA | ... | ... |
| SAT | ... | ... |
| Scholarship | ... | ... |
| Total Students | ... | ... |
| International % | ... | ... |

   - Only include rows where at least one university has data
   - NULL values → "N/A"

3. **QS Performance Breakdown** — If `score_details` is available, add a SECOND table:

| QS Indicator | [University 1] | [University 2] |
|---|---|---|
| Academic Reputation | 99.5/100 (#2) | 98.1/100 (#5) |
| Employer Reputation | 95.0/100 (#8) | 92.3/100 (#12) |
| Citations per Faculty | ... | ... |
| Faculty Student Ratio | ... | ... |
| International Faculty | ... | ... |
| International Students | ... | ... |

   - Parse the `score_details` field (format: "Name: X/100 (world rank #Y) | ...")
   - Show Score/100 and world rank (#N) in each cell
   - **Bold** the WINNER (higher score) in each row
   - Only include indicators that exist in the data
   - Place this table under header "### QS Performance Breakdown"

4. After the tables, write a BRIEF assessment (4-6 sentences):
   - Financial comparison (which is cheaper, value proposition)
   - Academic comparison (selectivity, requirements difference)
   - Key differentiator (what makes each unique)

5. Recommendations:
   - Best for strong applicants: [Name] — [reason]
   - Best value: [Name] — [reason]

6. Proactive follow-up: "Want me to check scholarship details?" or "Add another university to compare?"

RULES:
- Do NOT write individual university blocks before the table
- Keep column widths consistent
- If user has a profile, note which university is a better fit and why
- Maximum response: ~30 lines
"""
 