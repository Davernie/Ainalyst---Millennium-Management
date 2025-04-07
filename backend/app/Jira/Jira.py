import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

def get_jira_description():
    jira_server = os.getenv('JIRA_SERVER')
    jira_email = os.getenv('JIRA_EMAIL')
    jira_API_token = os.getenv('JIRA_API_TOKEN')
    issue_key = os.getenv('BRANCH_NAME')

    if not jira_server or not jira_email or not jira_API_token or not issue_key:
        raise ValueError("One or more JIRA credentials are missing.")

    jira = JIRA(server=jira_server, basic_auth=(jira_email, jira_API_token))
    issue = jira.issue(issue_key)
    description = issue.fields.description
    print(f"Issue Description: {description}")
    return description
    

# Just used to test the function
if __name__ == "__main__":
    get_jira_description()