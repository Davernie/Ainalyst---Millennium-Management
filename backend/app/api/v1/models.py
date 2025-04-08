from pydantic import BaseModel

class JiraCredentials(BaseModel):
    jiraServer: str
    jiraEmail: str
    jiraApiToken: str
    issueKey: str