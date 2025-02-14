# this is Eimer's work but Alex had trouble with the merge request to merge Eimer's branch into his so he just copied everything manually
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from ast_parser.astParser import astParser
from fastapi.responses import JSONResponse

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
    ast_parser = astParser()
    ast_issues = ast_parser.analyze(code)

    # Run PEP8 compliance check
    pep8_issues = run_pep8_linter(code)

    response_data = {
        "AST Issues": ast_issues if ast_issues else "No AST issues found.",
        "PEP8 Issues": pep8_issues
    }

    # Determine the appropriate HTTP status code
    if "No AST issues found." in response_data["AST Issues"] and "No PEP8 issues found." in response_data[
        "PEP8 Issues"]:
        status_code = 204  # OK
    elif "Neither Ruff nor Flake8 is installed." in response_data["PEP8 Issues"]:
        status_code = 500  # Internal Server Error
    else:
        status_code = 200  # OK, but with issues

    return JSONResponse(content=response_data, status_code=status_code)