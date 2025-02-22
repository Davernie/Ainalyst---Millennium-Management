from jira import JIRA

jira_server = 'https://tcd-team-ayl4vbq6.atlassian.net'
jira_email = 'eortiz@tcd.ie'
jira_API_token = 'ATATT3xFfGF0PxUqDBsfSo0R8xfAzKFwl304-8vvAQBbK1CXuC_QjOiksUShNNpZpEjWy6xkP6BTY3I_SaZz6XrxySwuqaiQaDrZbcctBFsjM1Q4tpK7snQ0XTjSHnh8LUJRnWOgqVuy2F0onEq9eai6kui6LEUyo5G9Ru9JqgQx0qj344lpGGU=1F6A92DB'
issue_key = 'AUT-2'

jira = JIRA(server=jira_server, basic_auth=(jira_email, jira_API_token))
issue = jira.issue(issue_key)

print(f"Issue Description: {issue.fields.description}")