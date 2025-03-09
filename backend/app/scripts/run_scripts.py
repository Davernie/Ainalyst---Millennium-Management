import argparse

from backend.app.services.ast_parsing_service import astParser
from backend.app.services.code_smells_service import check_code_smell
from backend.app.services.liniting_service import run_pep8_linter


def analyze_code(code):
    """Analyze Python code for AST issues and PEP8 violations."""

    # Run AST analysis
    ast_parser = astParser()
    ast_issues = ast_parser.analyze(code)

    # Run PEP8 compliance check
    pep8_issues = run_pep8_linter(code)

    code_smells = check_code_smell(code)

    # # Store the response in the database
    # result = db.execute(
    #     response_data.insert().values(
    #         timestamp=datetime.utcnow(),
    #         code=code,
    #         report_response=json.dumps({
    #             "AST Issues": ast_issues if ast_issues else "No AST issues found.",
    #             "PEP8 Issues": pep8_issues,
    #             "Code Smells": code_smells  # todo: Once I have API KEY, we can add code_smells
    #         })
    #     ).returning(response_data.c.id)
    # )
    # db.commit()


    # inserted_id = result.fetchone()[0]  # Fetch the id from the result tuple

    return {
        #"Status": f"Successfully Added information in Database with id: {inserted_id}",
        "Status": "Successfully Parsed, but not added to db",
        "AST Issues": ast_issues if ast_issues else "No AST issues found.",
        "PEP8 Issues": pep8_issues,
        "Code Smells": code_smells
    }




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to run Linter, Parser & Code Smell Checker")
    parser.add_argument("--filePath", type=str, help="First argument")
    args = parser.parse_args()
    print("Trying to open file: ", args.filePath)
    try:
        with open(args.filePath, "r") as file:
            code = file.read()
            result = analyze_code(code)
            print(result)

    except FileNotFoundError:
        print("Error: File not found.")

