import os
from dotenv import load_dotenv
from jira import JIRA\

load_dotenv()

jira_server = os.getenv('JIRA_SERVER')
jira_email = os.getenv('JIRA_EMAIL')
jira_API_token = os.getenv('JIRA_API_TOKEN')
issue_key = os.getenv('BRANCH_NAME')

jira = JIRA(server=jira_server, basic_auth=(jira_email, jira_API_token))
issue = jira.issue(issue_key)

print(f"Issue Description: {issue.fields.description}")