"""
SQL_RULES + SQL_EXAMPLES — Rules and few-shot examples for Text-to-SQL generation.
"""

SQL_RULES = """
### SQL RULES (MANDATORY):

1. CONTEXT RESOLUTION:
   - If the current question mentions a new country/region, use that (OVERRIDE history).
   - If the current question uses pronouns ("it", "that university", "còn", "thêm") or
     asks about an attribute without naming a university → resolve from CONVERSATION HISTORY
     or CURRENT CONTEXT block. Re-use the same university/country from recent context.
   - Example: History="MIT in US", Current="What about scholarships?" → SQL targets MIT.

2. SELECT enough columns — ALWAYS include:
   SELECT u.id, u.name, u.rank_int, u.overall_score, u.city,
          c.name AS country_name,
          d.fee, d.scholarship, d.total_stu, d.inter_total,
          d.domestic, d.international, d.ug_rate, d.pg_rate,
          d.english_test, d.academic_test,
          e.IELTS, e.TOEFL, e.GPA, e.SAT, e.GRE, e.GMAT,
          sc.score_details
   NEVER select only the university name.

3. Required JOINs:
   - Always: JOIN countries c ON c.id = u.country_id
   - Tuition/students: LEFT JOIN detail_infors d ON d.university_id = u.id
   - Entry requirements (general queries): LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1
   - Entry requirements (when user asks about entry/requirements/IELTS/GPA/SAT/TOEFL):
     Use TWO separate JOINs to get both Bachelor and Master data in one row per university:
     LEFT JOIN entry_infor e_ug ON e_ug.university_id = u.id AND e_ug.degree_type = 1
     LEFT JOIN entry_infor e_pg ON e_pg.university_id = u.id AND e_pg.degree_type = 2
     SELECT: e_ug.IELTS AS ug_IELTS, e_ug.TOEFL AS ug_TOEFL, e_ug.GPA AS ug_GPA,
             e_ug.SAT AS ug_SAT, e_ug.ACT AS ug_ACT,
             e_pg.IELTS AS pg_IELTS, e_pg.TOEFL AS pg_TOEFL, e_pg.GPA AS pg_GPA,
             e_pg.GRE AS pg_GRE, e_pg.GMAT AS pg_GMAT
   - Description/text: LEFT JOIN university_texts ut ON ut.university_id = u.id
   - Structured scholarships (ONLY when user asks about scholarships):
     LEFT JOIN scholarships s ON s.university_id = u.id
     Use GROUP_CONCAT(s.name) AS scholarship_names, GROUP_CONCAT(s.value) AS scholarship_values
   - QS scores/rankings: ALWAYS include this subquery join:
     LEFT JOIN (
       SELECT s.university_id,
              GROUP_CONCAT(
                CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')')
                ORDER BY s.score DESC SEPARATOR ' | '
              ) AS score_details
       FROM scores s
       JOIN indicators i ON i.id = s.indicator_id
       GROUP BY s.university_id
     ) sc ON sc.university_id = u.id

4. Prioritise complete data (Weighted Sort):
   When there is NO explicit ranking/top request, start ORDER BY with:
   CASE WHEN d.fee IS NOT NULL AND (e.IELTS IS NOT NULL OR e.GPA IS NOT NULL) THEN 0 ELSE 1 END ASC
   Then add the user's criterion (e.g., cheapest -> d.fee ASC).
   EXCEPTION: If user asks "Top N" or "best" → skip this, use ORDER BY u.rank_int ASC directly.

5. RANKING / TOP:
   - rank_int lower = better. Top N → ORDER BY u.rank_int ASC LIMIT N
   - No rank preference → ORDER BY u.overall_score DESC

6. HARD FILTERS (use in WHERE):
   - Country: c.name LIKE '%{English name}%'
   - Region: c.region_id = {1|2|3|4|5|6}
             Mapping: 1=Asia, 2=Europe, 3=North America, 4=Latin America, 5=Oceania, 6=Africa
             Example: "universities in Asia" → WHERE c.region_id = 1
   - Has scholarship: d.scholarship = 1
   - Scholarship value filter: NOT supported (value is stored as text with currency symbol e.g. '$5,000', '£15,000'). If user asks for scholarships >= X, filter by d.scholarship = 1 only and let AI note the limitation.
   - Tuition range: d.fee < X (only when user explicitly states a max budget)

7. SOFT FILTERS (do NOT filter in WHERE — just SELECT, let AI interpret after):
   - Specific IELTS/TOEFL/GPA/SAT score thresholds
   - "No English certificate", "low GPA", "health issues"

8. LIMIT: Always add LIMIT 20 unless user specifies a different number.

9. Return format — ONLY valid JSON, no markdown:
   {"sql": "...", "explanation": "..."}
   OR if the question is too vague to generate meaningful SQL:
   {"sql": "", "needs_clarification": true, "suggestion": "Please specify a country or field of study"}

10. USER PROFILE (when provided):
    Use scores as SOFT thresholds in ORDER BY (prefer universities whose
    requirements <= user's score). Do NOT hard-filter on profile scores.
    Example: IELTS 7.5, GPA 3.8:
      ORDER BY
        CASE WHEN e.IELTS IS NOT NULL AND CAST(e.IELTS AS DECIMAL(4,1)) <= 7.5 THEN 0
             WHEN e.IELTS IS NULL THEN 1 ELSE 2 END ASC,
        CASE WHEN e.GPA IS NOT NULL AND CAST(e.GPA AS DECIMAL(3,2)) <= 3.8 THEN 0
             WHEN e.GPA IS NULL THEN 1 ELSE 2 END ASC,
        u.rank_int ASC

11. ENTRY REQUIREMENTS for a SPECIFIC UNIVERSITY:
    When asking about entry requirements for a named university, use the TWO-JOIN approach from rule 3
    (e_ug for Bachelor, e_pg for Master) so both levels appear in a single row.
    SELECT: e_ug.IELTS AS ug_IELTS, e_ug.TOEFL AS ug_TOEFL, e_ug.GPA AS ug_GPA, e_ug.SAT AS ug_SAT, e_ug.ACT AS ug_ACT,
            e_pg.IELTS AS pg_IELTS, e_pg.TOEFL AS pg_TOEFL, e_pg.GPA AS pg_GPA, e_pg.GRE AS pg_GRE, e_pg.GMAT AS pg_GMAT.

12. MAJOR / SUBJECT / FIELD OF STUDY QUERIES:
    When user mentions a specific major/subject/discipline:
    - Add: JOIN university_majors um ON um.university_id = u.id
           JOIN majors m ON m.id = um.major_id
    - Filter: WHERE m.name LIKE '%{keyword}%'
    - SELECT: m.name AS major_name
    - Mapping:
        "Computer Science"/"CS"/"IT" → m.name LIKE '%Computer Science%'
        "Data Science"/"AI"/"Machine Learning" → m.name LIKE '%Data Science%'
        "Electrical Engineering"/"EEE" → m.name LIKE '%Electrical and Electronic%'
        "Civil Engineering" → m.name LIKE '%Civil and Structural%'
        "Mechanical Engineering" → m.name LIKE '%Mechanical%'
        "Chemical Engineering" → m.name LIKE '%Chemical%'
        "Petroleum Engineering" → m.name LIKE '%Petroleum%'
        "Mining Engineering" → m.name LIKE '%Mining%'
    - List majors: GROUP_CONCAT(m.name) AS majors_list, GROUP BY u.id
    - Do NOT join university_majors for general queries without a field/major mention.

13. FOLLOW-UP / PRONOUN RESOLUTION:
    If user says "it", "that university", "what about", "how about"
    without naming a new university → re-use the university/country from CURRENT CONTEXT.
    If CURRENT CONTEXT says "FOCUS: MIT, United States" and user asks "what about fees?"
    → Generate SQL targeting MIT specifically.

14. INCREMENTAL COMPARE:
    If history contains a comparison AND user adds another university name,
    generate SQL for ALL universities (previous + new).
"""

SQL_EXAMPLES = r"""
### EXAMPLES:

User: "What is the IELTS requirement for MIT?"
{"sql": "SELECT u.id, u.name, u.rank_int, c.name AS country_name, e.degree_type, e.SAT, e.GRE, e.GMAT, e.ACT, e.GPA, e.TOEFL, e.IELTS FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN entry_infor e ON e.university_id = u.id WHERE u.name LIKE '%MIT%' OR u.name LIKE '%Massachusetts Institute%'", "explanation": "All entry requirements for MIT across all degree types"}

User: "Top 5 best universities in the US"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.total_stu, d.inter_total, d.domestic, d.international, d.ug_rate, d.pg_rate, d.english_test, e.IELTS, e.TOEFL, e.GPA, e.SAT, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE c.name LIKE '%United States%' ORDER BY u.rank_int ASC LIMIT 5", "explanation": "Top 5 US universities by rank"}

User: "Compare MIT and Stanford"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.total_stu, d.inter_total, d.domestic, d.international, d.ug_rate, d.pg_rate, d.english_test, e.IELTS, e.TOEFL, e.GPA, e.SAT, ut.about, ut.scholarships, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN university_texts ut ON ut.university_id = u.id LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE u.name LIKE '%MIT%' OR u.name LIKE '%Massachusetts Institute%' OR u.name LIKE '%Stanford%'", "explanation": "Full data for MIT and Stanford"}

User: "Cheapest universities in Germany"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.TOEFL, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE c.name LIKE '%Germany%' ORDER BY CASE WHEN d.fee IS NOT NULL THEN 0 ELSE 1 END ASC, d.fee ASC LIMIT 20", "explanation": "German universities ordered cheapest first"}

User: "Universities in Asia with scholarship and tuition under 20000 USD"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE c.region_id = 1 AND d.scholarship = 1 AND d.fee < 20000 ORDER BY u.rank_int ASC LIMIT 20", "explanation": "Asian universities (region_id=1) with scholarship and fee < 20000"}

USER PROFILE: IELTS=7.5, GPA=3.8 | User: "Suggest universities that fit my profile"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.total_stu, d.english_test, e.IELTS, e.TOEFL, e.GPA, e.SAT, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id ORDER BY CASE WHEN e.IELTS IS NOT NULL AND CAST(e.IELTS AS DECIMAL(4,1)) <= 7.5 THEN 0 WHEN e.IELTS IS NULL THEN 1 ELSE 2 END ASC, CASE WHEN e.GPA IS NOT NULL AND CAST(e.GPA AS DECIMAL(3,2)) <= 3.8 THEN 0 WHEN e.GPA IS NULL THEN 1 ELSE 2 END ASC, u.rank_int ASC LIMIT 20", "explanation": "Universities matching profile: IELTS<=7.5, GPA<=3.8"}

User: "Top universities for Computer Science"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, m.name AS major_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.TOEFL, e.GPA FROM universities u JOIN countries c ON c.id = u.country_id JOIN university_majors um ON um.university_id = u.id JOIN majors m ON m.id = um.major_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 WHERE m.name LIKE '%Computer Science%' ORDER BY u.rank_int ASC LIMIT 20", "explanation": "Top universities QS-ranked in Computer Science"}

User: "What universities are good?"
{"sql": "", "needs_clarification": true, "suggestion": "Could you narrow it down? Which country or region are you interested in? Any specific major or budget in mind?"}

CONTEXT: "FOCUS: MIT" | User: "What about scholarships?"
{"sql": "SELECT u.id, u.name, u.rank_int, c.name AS country_name, d.fee, d.scholarship, ut.scholarships, s.name AS scholarship_name, s.value, s.duration, s.criteria FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN university_texts ut ON ut.university_id = u.id LEFT JOIN scholarships s ON s.university_id = u.id WHERE u.name LIKE '%MIT%' OR u.name LIKE '%Massachusetts Institute%'", "explanation": "Scholarship details for MIT (resolved from context)"}

### AMBIGUOUS / VAGUE QUERIES → needs_clarification:

User: "Which one is better?"
{"sql": "", "needs_clarification": true, "suggestion": "Which universities would you like me to compare? Please name at least two."}

User: "Tell me more"
{"sql": "", "needs_clarification": true, "suggestion": "Could you clarify what you'd like to know more about? A specific university, entry requirements, scholarships, or rankings?"}

User: "Help me choose"
{"sql": "", "needs_clarification": true, "suggestion": "Happy to help! What are your preferences? For example: country/region, field of study, budget, or your test scores (IELTS, GPA, etc.)?"}

User: "Any suggestions?"
{"sql": "", "needs_clarification": true, "suggestion": "Could you share more context? Which country or region interests you? Do you have a preferred major or a budget range?"}

### IMPLICIT INTENT / INDIRECT PHRASING (SOFT vs HARD filter distinction):

User: "I don't have IELTS, can I still study abroad?"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.TOEFL, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id ORDER BY CASE WHEN d.fee IS NOT NULL THEN 0 ELSE 1 END ASC, u.rank_int ASC LIMIT 20", "explanation": "Fetch all universities with entry data — do NOT add WHERE e.IELTS IS NULL; AI interprets from english_test and IELTS columns"}

User: "My GPA is only 2.8. Are there universities I can get into?"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id ORDER BY CASE WHEN e.GPA IS NOT NULL AND CAST(e.GPA AS DECIMAL(3,2)) <= 2.8 THEN 0 WHEN e.GPA IS NULL THEN 1 ELSE 2 END ASC, u.rank_int ASC LIMIT 20", "explanation": "GPA 2.8 is a SOFT threshold — sort by fit, never hard-filter with WHERE e.GPA <= 2.8"}

User: "I have a budget of 15000 USD per year for tuition"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE d.fee < 15000 ORDER BY u.rank_int ASC LIMIT 20", "explanation": "Budget is an explicit HARD filter — use WHERE d.fee < 15000"}

User: "Which country is the most affordable to study in?"
{"sql": "SELECT c.name AS country_name, COUNT(u.id) AS uni_count, ROUND(AVG(d.fee), 0) AS avg_fee, MIN(d.fee) AS min_fee FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id WHERE d.fee IS NOT NULL GROUP BY c.name ORDER BY avg_fee ASC LIMIT 15", "explanation": "Aggregate: countries ranked by average tuition — no individual university rows needed"}

### FOLLOW-UP / CONTEXT RESOLUTION:

CONTEXT: "FOCUS: University of Toronto" | User: "What about their scholarships?"
{"sql": "SELECT u.id, u.name, u.rank_int, c.name AS country_name, d.fee, d.scholarship, ut.scholarships, s.name AS scholarship_name, s.value, s.duration, s.criteria FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN university_texts ut ON ut.university_id = u.id LEFT JOIN scholarships s ON s.university_id = u.id WHERE u.name LIKE '%University of Toronto%'", "explanation": "Resolve 'their' from context → University of Toronto scholarships"}

CONTEXT: "FOCUS: ETH Zurich, Imperial College London" | User: "Add UCL to the comparison"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.total_stu, d.inter_total, d.english_test, e.IELTS, e.TOEFL, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE u.name LIKE '%ETH Zurich%' OR u.name LIKE '%Imperial College%' OR u.name LIKE '%UCL%' OR u.name LIKE '%University College London%'", "explanation": "Incremental compare — include all previous universities plus the new one (Rule 14)"}

CONTEXT: "discussed Australia" | User: "How about Canada instead?"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE c.name LIKE '%Canada%' ORDER BY u.rank_int ASC LIMIT 20", "explanation": "New country 'Canada' mentioned → OVERRIDE history, ignore Australia (Rule 1)"}

### MASTER'S / POSTGRADUATE:

User: "Master's programs in the UK — what are the GRE requirements?"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.english_test, e.degree_type, e.IELTS, e.TOEFL, e.GPA, e.GRE, e.GMAT, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 2 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE c.name LIKE '%United Kingdom%' ORDER BY CASE WHEN d.fee IS NOT NULL THEN 0 ELSE 1 END ASC, u.rank_int ASC LIMIT 20", "explanation": "UK Master's degree_type=2 — GRE is SOFT filter, AI interprets values from results"}

### MULTI-CRITERIA / COMBINED FILTERS:

User: "Affordable universities in Europe with scholarships for international students"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.inter_total, d.international, d.english_test, e.IELTS, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE c.region_id = 2 AND d.scholarship = 1 ORDER BY CASE WHEN d.fee IS NOT NULL THEN 0 ELSE 1 END ASC, d.fee ASC, u.rank_int ASC LIMIT 20", "explanation": "European (region_id=2) universities with scholarship, sorted by cheapest then rank"}

User: "Universities with the most international students in Oceania"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.total_stu, d.inter_total, d.international, d.english_test, e.IELTS, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE c.region_id = 5 AND d.inter_total IS NOT NULL ORDER BY d.inter_total DESC LIMIT 20", "explanation": "Oceania (region_id=5) universities sorted by most international students"}

User: "I want to study Data Science. What are my options in North America?"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, m.name AS major_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id JOIN university_majors um ON um.university_id = u.id JOIN majors m ON m.id = um.major_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE m.name LIKE '%Data Science%' AND c.region_id = 3 ORDER BY u.rank_int ASC LIMIT 20", "explanation": "Data Science programs in North America (region_id=3) — major join required"}

USER PROFILE: IELTS=6.5, GPA=3.2 | User: "I want to study in Singapore or South Korea"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE c.name LIKE '%Singapore%' OR c.name LIKE '%Korea%' ORDER BY CASE WHEN e.IELTS IS NOT NULL AND CAST(e.IELTS AS DECIMAL(4,1)) <= 6.5 THEN 0 WHEN e.IELTS IS NULL THEN 1 ELSE 2 END ASC, CASE WHEN e.GPA IS NOT NULL AND CAST(e.GPA AS DECIMAL(3,2)) <= 3.2 THEN 0 WHEN e.GPA IS NULL THEN 1 ELSE 2 END ASC, u.rank_int ASC LIMIT 20", "explanation": "Singapore or Korea universities sorted by profile fit (IELTS<=6.5, GPA<=3.2) — multiple countries use OR in WHERE"}
"""
 