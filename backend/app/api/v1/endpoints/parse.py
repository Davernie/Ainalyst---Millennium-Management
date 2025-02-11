from fastapi import APIRouter
from pydantic import BaseModel

from services.ast_parsing_service import astParser
from services.liniting_service import run_pep8_linter

from backend.app.services.code_smells_service import check_code_smell

router = APIRouter()

class CodeInput(BaseModel):
    code: str

@router.post("/analyze", status_code=200)
async def analyze_code(data: CodeInput):
    """Analyze Python code for AST issues and PEP8 violations."""
    code = data.code

    # Run AST analysis
    ast_parser = astParser()
    ast_issues = ast_parser.analyze(code)

    # Run PEP8 compliance check
    pep8_issues = run_pep8_linter(code)

    code_smells = check_code_smell(code)

    return {
        "AST Issues": ast_issues if ast_issues else "No AST issues found.",
        "PEP8 Issues": pep8_issues,
        "Code Smells": code_smells
    }

