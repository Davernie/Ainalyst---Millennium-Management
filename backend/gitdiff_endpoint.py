import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Pydantic model to accept the repository URL
class GitProject(BaseModel):
    repo_url: str  # Replace with project repository URL from frontend
    token: str     # Replace with project repo token from frontend 

@app.post("/analyze-diff/")
async def analyze_diff(data: GitProject):
    """Analyze git diff from the user's GitLab project repository."""
    try:
        # Clones the repository from GitLab using subprocess
        repo_url = data.repo_url
        token = data.token
        
        # Constructs the URL with token
        auth_repo_url = repo_url.replace("https://", f"https://{data.repo_url.split('/')[0]}:{token}@")

        repo_directory = "./user_repo"  # Local directory to clone the repo into

        # Clones the repository
        result = subprocess.run(
            ["git", "clone", auth_repo_url, repo_directory],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Error cloning the repository")

        diff_result = subprocess.run(
            ["git", "-C", repo_directory, "diff", "HEAD"],
            capture_output=True,
            text=True
        )

        if diff_result.returncode != 0:
            raise HTTPException(status_code=500, detail="Error fetching git diff")

        # Define the file path where the diff will be saved
        diff_file_path = "./git_diff_output.txt"
        
        # Write the git diff output to the file
        with open(diff_file_path, "w") as diff_file:
            diff_file.write(diff_result.stdout)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing diff: {str(e)}")