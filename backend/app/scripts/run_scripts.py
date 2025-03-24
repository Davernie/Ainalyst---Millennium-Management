import argparse
import json
from datetime import datetime
from sqlalchemy import create_engine, Table, MetaData, insert
from sqlalchemy.orm import sessionmaker

from backend.app.services.ast_parsing_service import astParser
from backend.app.services.code_smells_service import check_code_smell
from backend.app.services.liniting_service import run_pep8_linter

# Database connection setup
DATABASE_URL = "postgresql://avnadmin:AVNS_d4bV5orCyjUIYKdkJiQ@pg-298e7c66-senthilnaveen003-3105.k.aivencloud.com:26260/defaultdb?sslmode=require"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
metadata = MetaData()
response_data = Table("response_data", metadata, autoload_with=engine)


def analyze_code(code):
    """Analyze Python code for AST issues and PEP8 violations."""
    ast_parser = astParser()
    ast_issues = ast_parser.analyze(code)
    pep8_issues = run_pep8_linter(code)
    code_smells = check_code_smell(code)

    return {
        "AST Issues": ast_issues if ast_issues else "No AST issues found.",
        "PEP8 Issues": pep8_issues,
        "Code Smells": code_smells
    }


def save_to_db(code, analysis_result):
    """Save analysis result to the database and return the inserted ID."""
    db = SessionLocal()
    try:
        stmt = insert(response_data).values(
            username="Gitlab CI",
            filename="test",
            timestamp=datetime.utcnow(),
            code=json.dumps(code),
            report_response=json.dumps(analysis_result)
        ).returning(response_data.c.id)

        result = db.execute(stmt)
        db.commit()
        inserted_id = result.fetchone()[0]  # Fetch inserted ID
        return inserted_id
    except Exception as e:
        db.rollback()
        print(f"Database insertion failed: {e}")
        return None
    finally:
        db.close()


def format_analysis_results(results, inserted_id):
    """Format and print the analysis results with the inserted database ID."""
    print("# Code Analysis Report\n")
    print(f"## Status\nSuccessfully Added to Database with ID: {inserted_id}\n")
    print("## AST Issues")
    print("\n".join(f"- {issue}" for issue in results["AST Issues"]) if results[
        "AST Issues"] else "- No AST issues found.")
    print("\n## PEP8 Compliance")
    print(results["PEP8 Issues"].strip() if results["PEP8 Issues"] else "All checks passed!\n")
    print("\n## Code Smells")
    print(results["Code Smells"].strip() if results["Code Smells"] else "No code smells detected.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to run Linter, Parser & Code Smell Checker")
    parser.add_argument("--filePath", type=str, help="Path to the file to analyze")
    args = parser.parse_args()

    try:
        with open(args.filePath, "r") as file:
            code = file.read()
            result = analyze_code(code)
            inserted_id = save_to_db(code, result)
            if inserted_id:
                format_analysis_results(result, inserted_id)
            else:
                print("Error: Could not save results to database.")
    except FileNotFoundError:
        print("Error: File not found.")
