import requests
import re

GITLAB_TOKEN = "your_gitlab_token"
JIRA_EMAIL = "your_jira_email"
JIRA_TOKEN = "your_jira_token"
JIRA_BASE_URL = "https://your-domain.atlassian.net"
GITLAB_PROJECT_ID = "your_project_id"


def get_latest_commits():
    url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/repository/commits"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    response = requests.get(url, headers=headers)
    return response.json()


def transition_jira_issue(issue_key):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (JIRA_EMAIL, JIRA_TOKEN)
    payload = {
        "transition": {"id": "21"}  
    }
    response = requests.post(url, json=payload, headers=headers, auth=auth)
    return response.status_code

def main():
    commits = get_latest_commits()
    for commit in commits:
        message = commit["message"]
        
        match = re.search(r"([A-Z]+-\d+)", message)
        if match:
            issue_key = match.group(1)
            print(f"Transitioning {issue_key} to In Progress...")
            status = transition_jira_issue(issue_key)
            if status == 204:
                print(f"Successfully transitioned {issue_key}")
            else:
                print(f"Failed to transition {issue_key}")

if __name__ == "__main__":
    main()