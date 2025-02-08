from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from backend.ast_parser.astParser import ASTParser  

app = FastAPI()

class CodeInput(BaseModel):
    code: str  # User submits Python code as a string

def run_pep8_linter(code: str):
    """Run PEP8 compliance check using Ruff or Flake8."""
    with open("temp_code.py", "w") as f:
        f.write(code)
    
    try:
        # Use Ruff (recommended) or fallback to Flake8
        result = subprocess.run(["ruff", "check", "temp_code.py"], capture_output=True, text=True)
        return result.stdout if result.stdout else "No PEP8 issues found."
    except FileNotFoundError:
        try:
            result = subprocess.run(["flake8", "temp_code.py"], capture_output=True, text=True)
            return result.stdout if result.stdout else "No PEP8 issues found."
        except FileNotFoundError:
            return "Neither Ruff nor Flake8 is installed."

@app.post("/analyze/")
async def analyze_code(data: CodeInput):
    """Analyze Python code for AST issues and PEP8 violations."""
    code = data.code

    # Run AST analysis
    ast_parser = ASTParser()
    ast_issues = ast_parser.analyze(code)

    # Run PEP8 compliance check
    pep8_issues = run_pep8_linter(code)

    return {
        "AST Issues": ast_issues if ast_issues else "No AST issues found.",
        "PEP8 Issues": pep8_issues
    }
