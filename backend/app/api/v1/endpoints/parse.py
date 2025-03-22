# api/v1/parse.py
import json
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel


from backend.app.services.ast_parsing_service import astParser
from backend.app.services.liniting_service import run_pep8_linter
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.database.database import response_data

from backend.app.scripts.run_scripts import format_analysis_results
from backend.app.services.code_smells_service import check_code_smell

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)



class CodeInput(BaseModel):
    code: str
    userName: str  # Username of the user submitting the code
    fileName: str  # Name of the submitted file
@router.post("/analyze")
async def analyze_code(data: CodeInput,  db: Session = Depends(get_db)):
    """Analyze Python code for AST issues and PEP8 violations."""
    code = data.code
    userName = data.userName
    fileName = data.fileName
    # Run AST analysis
    ast_parser = astParser()
    ast_issues = ast_parser.analyze(code)
    # Run PEP8 compliance check
    pep8_issues = run_pep8_linter(code)
    code_smells = check_code_smell(code)
    # Store the response in the database

    try:
        print("sending to db")
        result = db.execute(
            response_data.insert().values(
                username=userName,
                filename=fileName,
                timestamp=datetime.utcnow(),
                code=code,
                report_response=json.dumps({
                    "AST Issues": ast_issues if ast_issues else "No AST issues found.",
                    "PEP8 Issues": pep8_issues,
                    "Code Smells": code_smells,
                })
            ).returning(response_data.c.id)
        )
        print("executed")
        db.commit()
        print("commited")
        inserted_id = result.fetchone()[0]  # Fetch the id from the result tuple
        print(f"Inserted into DB, ID: {inserted_id}")  # Debugging log
    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")  # Debugging log
        return {"error": f"Database insertion failed: {e}"}
    results = db.execute(select(response_data)).fetchall()
    print(f"Database contents after insert: {results}")  # Debugging log

    print()
    print()
    print()

    response = {
        "Status": f"Successfully Added information in Database with id: {inserted_id}",
        "id": inserted_id,  # Add the id explicitly here
        "AST Issues": ast_issues if ast_issues else "No AST issues found.",
        "PEP8 Issues": pep8_issues,
        "Code Smells": code_smells
    }
    format_analysis_results(response, inserted_id)
    return response


@router.get("/responses", status_code=200)
async def get_all_responses(db: Session = Depends(get_db)):
    """Retrieve all saved responses from the database."""
    results = db.execute(select(response_data)).fetchall()
    if results:
        return [
            {
                "id": row.id,
                "timestamp": row.timestamp,
                "code": row.code,
                "report_response": json.loads(row.report_response)
            }
            for row in results
        ]
    else:
        return [
            {
                "id": "N/A",
                "timestamp": "N/A",
                "code": "N/A",
                "report_response": "N/A"
            }
        ]


@router.post("/responses/{response_id}", status_code=200)
async def get_response_by_id(response_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific response by ID."""
    result = db.execute(select(response_data).where(response_data.c.id == response_id)).first()

    if not result:
        return [
            {
                "id": "N/A",
                "timestamp": "N/A",
                "code": "N/A",
                "report_response": "N/A"
            }
        ]

    return {
        "id": result.id,
        "timestamp": result.timestamp,
        "code": result.code,
        "report_response": json.loads(result.report_response)
    }

class ProgramInput(BaseModel):
    userName: str  # Username of the user submitting the code
    fileName: str # Name of the submitted file
@router.post("/getresponse/", status_code=200)
async def get_response_user_filename(data: ProgramInput, db: Session = Depends(get_db)):
    """Retrieve all responses by username and filename."""
    userName = data.userName
    fileName = data.fileName

    # Fetch all rows matching the username and filename
    result = db.execute(
        select(response_data).where(
            and_(response_data.c.username == userName, response_data.c.filename == fileName)
        )
    ).fetchall()  # Fetch all matching rows

    if not result:
        print("No result found")  # Debugging statement
        return [
            {
                "id": "N/A",
                "timestamp": "N/A",
                "code": "N/A",
                "report_response": "N/A"
            }
        ]

    # Map the results to a list of dictionaries to return
    formatted_results = [
        {
            "id": row.id,
            "timestamp": row.timestamp,
            "code": row.code,
            "report_response": row.report_response
        }
        for row in result
    ]

    print(f"Found {len(formatted_results)} results.")
    print(formatted_results)
    return formatted_results