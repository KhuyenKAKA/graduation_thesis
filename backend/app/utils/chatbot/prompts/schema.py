"""
SCHEMA_CONTEXT — MySQL table descriptions injected into the SQL generation prompt.
"""

SCHEMA_CONTEXT = """
### DATABASE SCHEMA (MySQL — universities_db):

Table: countries
  - id (PK, INT)
  - name (VARCHAR): English country name, e.g. 'United States', 'United Kingdom'

Table: universities
  - id (PK, INT)
  - name (VARCHAR): Full university name
  - region (ENUM): 'Asia','Europe','North America','Latin America','Oceania','Africa'
  - country_id (FK -> countries.id)
  - city (VARCHAR)
  - overall_score (FLOAT): QS-style overall score 0-100
  - rank_int (INT): Global rank number (lower = better)

Table: detail_infors          -- tuition, student counts, scholarships
  - university_id (FK -> universities.id)
  - fee (DOUBLE): Tuition fee in USD/year
  - scholarship (TINYINT 0/1): 1 = has scholarship
  - domestic (FLOAT): % domestic students
  - international (FLOAT): % international students
  - total_stu (INT): Total student enrollment
  - ug_rate (FLOAT): % undergraduate students
  - pg_rate (FLOAT): % postgraduate students
  - inter_total (INT): Total international students
  - inter_ug_rate (FLOAT): % international undergrads
  - inter_pg_rate (FLOAT): % international postgrads
  - english_test (VARCHAR): Accepted English tests info
  - academic_test (VARCHAR): Accepted academic tests info

Table: entry_infor            -- entry requirements
  - university_id (FK -> universities.id)
  - degree_type (INT): 1 = Bachelor, 2 = Master
  - SAT (VARCHAR), GRE (VARCHAR), GMAT (VARCHAR), ACT (VARCHAR)
  - GPA (VARCHAR), TOEFL (VARCHAR), IELTS (VARCHAR)

Table: university_texts       -- descriptive text
  - university_id (FK -> universities.id)
  - about (TEXT)
  - scholarships (TEXT): Scholarship descriptions
  - rankings_and_ratings (TEXT)
  - university_information (TEXT)

Table: scholarships           -- structured scholarship records (one row per scholarship)
  - id (PK, INT AUTO_INCREMENT)
  - university_id (FK -> universities.id)
  - name (TEXT): Scholarship name
  - value (DOUBLE): Annual award value in USD
  - duration (TEXT): Duration of the award, e.g. '4 years', '1 year'
  - criteria (TEXT): Eligibility criteria description

Table: score_types            -- category names for score groups
  - id (PK, INT)
  - name (VARCHAR): e.g. 'Research & Discovery', 'Employability', 'Global Engagement',
                         'Learning Experience', 'Sustainability'

Table: indicators             -- individual scoring criteria
  - id (PK, INT)
  - name (VARCHAR): e.g. 'Academic Reputation', 'Employer Reputation',
                         'Citations per Faculty', 'Faculty Student Ratio',
                         'International Student Ratio', 'International Research Network',
                         'International Faculty Ratio', 'Sustainability Score'

Table: scores                 -- per-university indicator scores (one row per indicator)
  - id (PK, INT)
  - university_id (FK -> universities.id)
  - indicator_id (FK -> indicators.id)
  - score_type_id (FK -> score_types.id)
  - rank_int (INT): World rank for this specific indicator (lower = better)
  - score (FLOAT): Score 0-100 for this indicator
  NOTE: Aggregate with GROUP_CONCAT when joining to universities table to avoid duplicate rows.

Table: majors                 -- academic disciplines tracked from QS Rankings by subject
  - id (PK, INT)
  - name (VARCHAR UNIQUE): Full subject name. Current values in DB:
      'Computer Science and Information Systems'
      'Data Science and Artificial Intelligence'
      'Engineering - Chemical'
      'Engineering - Civil and Structural'
      'Engineering - Electrical and Electronic'
      'Engineering - Mechanical'
      'Engineering - Mineral and Mining'
      'Engineering - Petroleum'

Table: university_majors      -- many-to-many: which universities are QS-ranked in which major
  - id (PK, INT)
  - university_id (FK -> universities.id)
  - major_id (FK -> majors.id)
  - title (VARCHAR): Original QS source name for the university (for verification only)
  - UNIQUE (university_id, major_id): one row per university-major pair
  NOTE: A university present in this table means QS has ranked it in that major.
        A university absent from this table may still offer that major — we just lack ranking data.
"""
 