"""
DOMAIN_POOR_PROMPT — When database has insufficient data for the query.
"""

DOMAIN_POOR_PROMPT = """{system_context}

---
SITUATION: User asked: "{message}"

Our database does NOT have sufficient detailed data (tuition/entry requirements are NULL or missing) for this query.

CONVERSATION HISTORY:
{history}

UNIVERSITIES FOUND (names only, data incomplete):
{found_schools}

YOUR TASK:
1. Briefly acknowledge the query and state that detailed data is limited in our database for this specific search.
2. If university names were found, mention them and note which data is missing.
3. Do NOT fabricate any numbers, fees, or requirements.
4. Invite the user to click the "Search Online" button for up-to-date info from official sources.
5. Suggest alternative queries that might yield better results from our database.

Keep the response to 4-6 lines. Be honest but helpful.
"""
 