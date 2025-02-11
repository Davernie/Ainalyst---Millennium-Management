import subprocess

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
