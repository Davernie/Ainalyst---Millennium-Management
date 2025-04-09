import json
import os
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pathlib import Path

from backend.app.services.ast_parsing_service import astParser
from backend.app.services.liniting_service import run_pep8_linter
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.database.database import response_data

from backend.app.scripts.run_scripts import format_analysis_results
from backend.app.services.code_smells_service import check_code_smell

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CodeInput(BaseModel):
    code: str
    userName: str  # Username of the user submitting the code
    fileName: str  # Name of the submitted file


@router.post("/analyze")
async def analyze_code(data: CodeInput, db: Session = Depends(get_db)):
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
                    "Code Smells": code_smells
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


@router.post("/analyze-codebase")
async def analyze_codebase(userName: str, db: Session = Depends(get_db)):
    """Analyze all Python files in the 'backend/codebase' directory."""

    current_dir = Path(__file__).resolve().parent
    backend_dir = current_dir.parent.parent.parent.parent
    directory_path = backend_dir / "codebase"
    directory_path = directory_path.resolve()

    logger.info(f"Using directory path: {directory_path}")
    response_list = []

    if not os.path.exists(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return []

    for root, _, files in os.walk(directory_path):
        logger.info(f"directory contains {files}")
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()

                # Run AST analysis
                ast_parser = astParser()
                ast_issues = ast_parser.analyze(code)

                # Run PEP8 compliance check
                pep8_issues = run_pep8_linter(code)
                code_smells = check_code_smell(code)

                try:
                    logger.info(f"Analyzing {file_path}")
                    result = db.execute(
                        response_data.insert().values(
                            username=userName,
                            filename=file,
                            timestamp=datetime.utcnow(),
                            code=code,
                            report_response=json.dumps({
                                "AST Issues": ast_issues if ast_issues else "No AST issues found.",
                                "PEP8 Issues": pep8_issues,
                                "Code Smells": code_smells,
                            })
                        ).returning(response_data.c.id)
                    )
                    db.commit()
                    inserted_id = result.fetchone()[0]
                    logger.info(f"Inserted {file} into DB with ID: {inserted_id}")

                    response = {
                        "Status": f"Successfully Added information in Database with id: {inserted_id}",
                        "filename": file,
                        "id": inserted_id,
                        "AST Issues": ast_issues if ast_issues else "No AST issues found.",
                        "PEP8 Issues": pep8_issues,
                        "Code Smells": code_smells
                    }
                    format_analysis_results(response, inserted_id)
                    response_list.append(response)

                except Exception as e:
                    db.rollback()
                    logger.error(f"Error inserting data for {file}: {e}")
                    response_list.append({"error": f"Database insertion failed for {file}: {e}"})
    logger.info(f"returning response {response_list}")
    return response_list


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
    fileName: str  # Name of the submitted file


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


@router.get("/analyze-latest", status_code=200)
async def analyze_latest(db: Session = Depends(get_db)):
    """Retrieve the latest saved response from the database by selecting the maximum id."""
    latest = db.execute(
        select(response_data).order_by(desc(response_data.c.id)).limit(1)
    ).first()

    if not latest:
        raise HTTPException(status_code=404, detail="No responses found")

    return {
        "id": latest.id,
        "timestamp": latest.timestamp,
        "code": latest.code,
        "report_response": json.loads(latest.report_response)
    }


from collections import Counter


@router.get("/common_issues/{user_name}", status_code=200)
async def get_common_issues(user_name: str, db: Session = Depends(get_db)):
    """Get the most common AST and PEP8 issues for a specific user.

    Args:
        user_name: Username to analyze (from URL path)
        db: Database session dependency
    """
    # Fetch all rows matching the username
    result = db.execute(
        select(response_data).where(response_data.c.username == user_name)
    ).fetchall()

    if not result:
        return {"message": "No submissions found for this user."}

    ast_issues_counter = Counter()
    pep8_issues_counter = Counter()

    for row in result:
        try:
            report = json.loads(row.report_response)
            ast_issues = report.get("AST Issues", "")
            pep8_issues = report.get("PEP8 Issues", "")

            # Normalize to a list
            if isinstance(ast_issues, str):
                ast_issues = ast_issues.split("\n")
            if isinstance(pep8_issues, str):
                pep8_issues = pep8_issues.split("\n")

            ast_issues = [issue.strip() for issue in ast_issues if issue.strip()]
            pep8_issues = [issue.strip() for issue in pep8_issues if issue.strip()]

            ast_issues_counter.update(ast_issues)
            pep8_issues_counter.update(pep8_issues)

        except Exception as e:
            print(f"Error processing report_response for row {row.id}: {e}")

    return {
        "user": user_name,
        "common_AST_Issues": ast_issues_counter.most_common(),
        "common_PEP8_Issues": pep8_issues_counter.most_common()
    }