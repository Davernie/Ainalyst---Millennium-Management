import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.ast_parsing_service import astParser
from services.liniting_service import run_pep8_linter
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.database import get_db
from database.database import response_data

from backend.app.services.code_smells_service import check_code_smell

router = APIRouter()

class CodeInput(BaseModel):
    code: str

@router.post("/analyze", status_code=200)
async def analyze_code(data: CodeInput,  db: Session = Depends(get_db)):
    """Analyze Python code for AST issues and PEP8 violations."""
    code = data.code

    # Run AST analysis
    ast_parser = astParser()
    ast_issues = ast_parser.analyze(code)

    # Run PEP8 compliance check
    pep8_issues = run_pep8_linter(code)

    #code_smells = check_code_smell(code)       #todo: Uncomment Once you have API KEY

    # Store the response in the database
    db.execute(
        response_data.insert().values(
            timestamp=datetime.utcnow(),
            code=code,
            report_response=json.dumps({
                "AST Issues": ast_issues if ast_issues else "No AST issues found.",
                "PEP8 Issues": pep8_issues,
                "Code Smells": "None" #todo: Once we have API KEY, we can add code_smells
            })
        )
    )
    db.commit()

    return {
        "AST Issues": ast_issues if ast_issues else "No AST issues found.",
        "PEP8 Issues": pep8_issues
        #"Code Smells": code_smells         #todo: Uncomment Once you have API KEY
    }


@router.get("/responses", status_code=200)
async def get_all_responses(db: Session = Depends(get_db)):
    """Retrieve all saved responses from the database."""
    results = db.execute(select(response_data)).fetchall()

    return [
        {
            "id": row.id,
            "timestamp": row.timestamp,
            "code": row.code,  # Already stored as a string
            "report_response": json.loads(row.report_response)  # Convert JSON string to dictionary
        }
        for row in results
    ]


@router.get("/responses/{response_id}", status_code=200)
async def get_response_by_id(response_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific response by ID."""
    result = db.execute(select(response_data).where(response_data.c.id == response_id)).first()

    if not result:
        raise HTTPException(status_code=404, detail="Response not found")

    return {
        "id": result.id,
        "timestamp": result.timestamp,
        "code": result.code,  # Already stored as a string
        "report_response": json.loads(result.report_response)  # Convert JSON string to dictionary
    }
