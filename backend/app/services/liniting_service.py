import subprocess
import argparse
import json

def run_pep8_linter(file_path: str, output_path: str):
    """
    Run PEP8 compliance check using Ruff or Flake8 on a given file.
    Output is saved to a JSON file for easy review in CI systems.
    """
    try:
        # Attempt Ruff with JSON output
        result = subprocess.run(
            ["ruff", "check", file_path, "--format", "json"],
            capture_output=True,
            text=True
        )

        # If Ruff ran successfully, write its output
        if result.stdout:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.stdout)
        else:
            # No output means no issues found
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json.dumps({"message": "No PEP8 issues found."}))
    except FileNotFoundError:
        # If Ruff not found, try Flake8 with JSON output
        try:
            result = subprocess.run(
                ["flake8", file_path, "--format=json"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result.stdout)
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps({"message": "No PEP8 issues found."}))
        except FileNotFoundError:
            # Neither Ruff nor Flake8 installed
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json.dumps({"error": "Neither Ruff nor Flake8 is installed."}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PEP8 linting using Ruff or Flake8.")
    parser.add_argument("--file", required=True, help="Path to the file to lint.")
    parser.add_argument("--output", required=True, help="Path to the output JSON file.")
    args = parser.parse_args()

    run_pep8_linter(args.file, args.output)
    print(f"PEP8 linting completed. Results saved to {args.output}.")
