import argparse
import json
import os
import socket
import socks
from datetime import datetime
from sqlalchemy import create_engine, Table, MetaData, insert
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from backend.app.services.ast_parsing_service import astParser
from backend.app.services.code_smells_service import check_code_smell
from backend.app.services.liniting_service import run_pep8_linter

# Database connection details
DATABASE_URL = "postgresql://avnadmin:AVNS_d4bV5orCyjUIYKdkJiQ@pg-298e7c66-senthilnaveen003-3105.k.aivencloud.com:26260/defaultdb?sslmode=require"

# SOCKS proxy configuration
SOCKS_PROXY_HOST = "socks-proxy.scss.tcd.ie"
SOCKS_PROXY_PORT = 1080

original_socket = socket.socket  # Save the original socket


def is_college_environment():
    """
    Check if a direct connection to the database is possible.
    Returns False if a direct connection is successful, True otherwise.
    """
    DB_HOST = "pg-298e7c66-senthilnaveen003-3105.k.aivencloud.com"
    DB_PORT = 26260
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex((DB_HOST, DB_PORT))
        s.close()
        return False if result == 0 else True
    except Exception:
        return True


def get_db_components():
    """
    Create and return a new SQLAlchemy engine, session, metadata, and response_data table.
    This function applies the SOCKS proxy (if needed) before creating the engine.
    """
    if is_college_environment():
        print("Using SOCKS proxy for database connection.")
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, SOCKS_PROXY_HOST, SOCKS_PROXY_PORT)
        socket.socket = socks.socksocket
    else:
        print("Connecting to database directly.")

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    metadata = MetaData()
    response_data = Table("response_data", metadata, autoload_with=engine)

    # Restore original socket after engine creation
    if is_college_environment():
        socket.socket = original_socket
    return engine, SessionLocal, metadata, response_data


def analyze_code(code):
    """Analyze Python code for AST issues, PEP8 violations, and code smells."""
    ast_parser = astParser()
    ast_issues = ast_parser.analyze(code)
    pep8_issues = run_pep8_linter(code)
    code_smells = check_code_smell(code)

    return {
        "AST Issues": ast_issues if ast_issues else "No AST issues found.",
        "PEP8 Issues": pep8_issues,
        "Code Smells": code_smells
    }


def save_to_db(filename, code, analysis_result):
    """Save analysis results to the database and return the inserted ID."""
    engine, SessionLocal, metadata, response_data = get_db_components()
    db = SessionLocal()
    try:
        stmt = insert(response_data).values(
            username="Gitlab CI",
            filename=filename,
            timestamp=datetime.utcnow(),
            code=json.dumps(code),
            report_response=json.dumps(analysis_result)
        ).returning(response_data.c.id)

        result = db.execute(stmt)
        db.commit()
        inserted_id = result.fetchone()[0]
        return inserted_id
    except Exception as e:
        db.rollback()
        print(f"Database insertion failed for {filename}: {e}")
        return None
    finally:
        db.close()


def format_analysis_results(filename, results, inserted_id):
    """Format and print the analysis results with the inserted database ID."""
    print(f"\n# Code Analysis Report for {filename}\n")
    print(f"## Status: Successfully Added to Database with ID: {inserted_id}\n")
    print("## AST Issues")
    print("\n".join(f"- {issue}" for issue in results["AST Issues"]) if results[
        "AST Issues"] else "- No AST issues found.")
    print("\n## PEP8 Compliance")
    print(results["PEP8 Issues"].strip() if results["PEP8 Issues"] else "All checks passed!\n")
    print("\n## Code Smells")
    print(results["Code Smells"].strip() if results["Code Smells"] else "No code smells detected.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to analyze all Python files in a given directory.")
    parser.add_argument("--dirPath", type=str, required=True, help="Path to the directory to analyze")
    args = parser.parse_args()

    directory_path = Path(args.dirPath).resolve()

    if not directory_path.exists() or not directory_path.is_dir():
        print("Error: Provided path is not a valid directory.")
        exit(1)

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                        result = analyze_code(code)
                        inserted_id = save_to_db(file, code, result)
                        if inserted_id:
                            format_analysis_results(file, result, inserted_id)
                        else:
                            print(f"Error: Could not save results for {file} to database.")
                except Exception as e:
                    print(f"Error processing {file}: {e}")
