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
   - Entry requirements: LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1
   - Description/text: LEFT JOIN university_texts ut ON ut.university_id = u.id
   - Structured scholarships (ONLY when user asks about scholarships):
     LEFT JOIN scholarships s ON s.university_id = u.id
     Use GROUP_CONCAT(s.name) AS scholarship_names, MIN(s.value) AS min_scholarship_value
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
   - Region: u.region = '{Asia|Europe|North America|Latin America|Oceania|Africa}'
   - Has scholarship: d.scholarship = 1
   - Scholarship value: s.value >= X (only when user asks for scholarship worth at least X)
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
    When asking about entry requirements for named universities, do NOT filter by degree_type.
    JOIN entry_infor WITHOUT AND e.degree_type = X so ALL degree levels return.
    Always SELECT: e.degree_type, e.SAT, e.GRE, e.GMAT, e.ACT, e.GPA, e.TOEFL, e.IELTS.

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
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.GPA, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id WHERE u.region = 'Asia' AND d.scholarship = 1 AND d.fee < 20000 ORDER BY u.rank_int ASC LIMIT 20", "explanation": "Asian universities with scholarship and fee < 20000"}

USER PROFILE: IELTS=7.5, GPA=3.8 | User: "Suggest universities that fit my profile"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, d.fee, d.scholarship, d.total_stu, d.english_test, e.IELTS, e.TOEFL, e.GPA, e.SAT, sc.score_details FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 LEFT JOIN (SELECT s.university_id, GROUP_CONCAT(CONCAT(i.name, ': ', ROUND(s.score,1), '/100 (world rank #', s.rank_int, ')') ORDER BY s.score DESC SEPARATOR ' | ') AS score_details FROM scores s JOIN indicators i ON i.id = s.indicator_id GROUP BY s.university_id) sc ON sc.university_id = u.id ORDER BY CASE WHEN e.IELTS IS NOT NULL AND CAST(e.IELTS AS DECIMAL(4,1)) <= 7.5 THEN 0 WHEN e.IELTS IS NULL THEN 1 ELSE 2 END ASC, CASE WHEN e.GPA IS NOT NULL AND CAST(e.GPA AS DECIMAL(3,2)) <= 3.8 THEN 0 WHEN e.GPA IS NULL THEN 1 ELSE 2 END ASC, u.rank_int ASC LIMIT 20", "explanation": "Universities matching profile: IELTS<=7.5, GPA<=3.8"}

User: "Top universities for Computer Science"
{"sql": "SELECT u.id, u.name, u.rank_int, u.overall_score, u.city, c.name AS country_name, m.name AS major_name, d.fee, d.scholarship, d.english_test, e.IELTS, e.TOEFL, e.GPA FROM universities u JOIN countries c ON c.id = u.country_id JOIN university_majors um ON um.university_id = u.id JOIN majors m ON m.id = um.major_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN entry_infor e ON e.university_id = u.id AND e.degree_type = 1 WHERE m.name LIKE '%Computer Science%' ORDER BY u.rank_int ASC LIMIT 20", "explanation": "Top universities QS-ranked in Computer Science"}

User: "trường nào tốt?"
{"sql": "", "needs_clarification": true, "suggestion": "Bạn quan tâm quốc gia/khu vực nào? Ngành học cụ thể? Ngân sách bao nhiêu?"}

CONTEXT: "FOCUS: MIT" | User: "còn học bổng thì sao?"
{"sql": "SELECT u.id, u.name, u.rank_int, c.name AS country_name, d.fee, d.scholarship, ut.scholarships, s.name AS scholarship_name, s.value, s.duration, s.criteria FROM universities u JOIN countries c ON c.id = u.country_id LEFT JOIN detail_infors d ON d.university_id = u.id LEFT JOIN university_texts ut ON ut.university_id = u.id LEFT JOIN scholarships s ON s.university_id = u.id WHERE u.name LIKE '%MIT%' OR u.name LIKE '%Massachusetts Institute%'", "explanation": "Scholarship details for MIT (resolved from context)"}
"""
 