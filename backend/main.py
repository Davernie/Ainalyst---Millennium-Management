# creating this was Eimer's work but Alex had trouble with the merge request to merge Eimer's branch into his so he just copied everything manually
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from ast_parser.astParser import astParser
from fastapi.responses import JSONResponse
from datetime import datetime
from pytz import utc
app = FastAPI()

class CodeInput(BaseModel):
    code: str  # User submits Python code as a string
    userName: str  # Username of the user submitting the code
    fileLocation: str  # Location of the file being analyzed

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
    userName = data.userName
    fileLocation = data.fileLocation
    timestamp = datetime.now(utc)

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

    try:
        conn = psycopg2.connect(database="resultsdb",
                                host='localhost',
                                port=5432)
        cursor = conn.cursor()
        if status_code == 200:
            cursor.execute(
                "INSERT INTO CodeAnalysis (username, date_and_time, filename, response_code, response, ai_response) VALUES (%s, %s, %s, %s, %s, %s)",
                (userName, timestamp, fileLocation, status_code, response_data, "Not yet implemented")
            )
        elif status_code == 204:
            cursor.execute(
                "INSERT INTO CodeAnalysis (username, date_and_time, filename, response_code, response, ai_response) VALUES (%s, %s, %s, %s, %s, %s)",
                (userName, timestamp, fileLocation, status_code, "No issues detected", "Not yet implemented")
            )
        else:
            cursor.execute(
                "INSERT INTO CodeAnalysis (username, date_and_time, filename, response_code, response, ai_response) VALUES (%s, %s, %s, %s, %s, %s)",
                (userName, timestamp, fileLocation, status_code, "API error", "Not yet implemented")
            )
        conn.commit()
        print("API response successfully stored in PostgreSQL!")
    except Exception as e:
        print("Database error:", e)
    finally:
        cursor.close()
        conn.close()

    return JSONResponse(content=response_data, status_code=status_code)