from fastapi import APIRouter, HTTPException
from backend.app.api.v1.models import JiraCredentials
from dotenv import load_dotenv, set_key
import os
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(__file__), '../../../../.env')

load_dotenv(dotenv_path=env_path)

@router.post("/update-env")
async def update_env(credentials: JiraCredentials):
    try:
        set_key(env_path, 'JIRA_SERVER', credentials.jiraServer, quote_mode="never")
        set_key(env_path, 'JIRA_EMAIL', credentials.jiraEmail, quote_mode="never")
        set_key(env_path, 'JIRA_API_TOKEN', credentials.jiraApiToken, quote_mode="never")
        set_key(env_path, 'BRANCH_NAME', credentials.issueKey, quote_mode="never")

        return {"message": "Environment variables updated successfully!"}
    except Exception as e:
        logger.error(f"Error updating environment variables: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
