from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import os
from typing import Optional

from AI.gitdiffs import analyze_git_diff

router = APIRouter()

class PRRequest(BaseModel):
    base_branch: Optional[str] = None
    target_branch: Optional[str] = None
    commit_id: Optional[str] = None

@router.post("/generate-pr")
async def generate_pr(data: PRRequest):
    try:
        # Get git diff
        if data.commit_id:
            cmd = ["git", "show", data.commit_id]
        elif data.base_branch and data.target_branch:
            cmd = ["git", "diff", f"{data.base_branch}..{data.target_branch}"]
        else:
            raise HTTPException(status_code=400, detail="Provide either commit_id or both base_branch and target_branch")

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Git error: {result.stderr}")

        diff = result.stdout

        # Run the existing LLM analysis
        analyze_git_diff(diff)

        # Read output file that analyze_git_diff writes to
        output_path = "git_diffs_report.txt"
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Analysis output file not found.")

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Heuristically split into title and description
        lines = content.split("\n", 1)
        title = lines[0].strip()
        description = lines[1].strip() if len(lines) > 1 else "No detailed description provided."

        return {"title": title, "description": description}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
