import ast
import argparse
import json

class astParser(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_FunctionDef(self, node):
        # Check for functions with empty bodies
        if node.body and isinstance(node.body[0], ast.Pass):
            self.issues.append(f"Warning: Function '{node.name}' has an empty body.")

        # Check for functions with arguments but no return statement
        if node.args.args and not any(isinstance(n, ast.Return) for n in ast.walk(node)):
            self.issues.append(f"Warning: Function '{node.name}' takes arguments but has no return statement.")

        self.generic_visit(node)

    def visit_If(self, node):
        # Detect dead code (if condition is a constant False, 0, None, or empty string)
        if isinstance(node.test, ast.Constant) and not node.test.value:
            self.issues.append("Warning: Detected dead code in an 'if' statement with a constant False condition.")
        elif isinstance(node.test, (ast.Num, ast.Str, ast.NameConstant)) and not bool(
            node.test.n if isinstance(node.test, ast.Num) else
            node.test.s if isinstance(node.test, ast.Str) else
            node.test.value
        ):
            self.issues.append(
                "Warning: Detected dead code in an 'if' statement with a constant False-equivalent condition."
            )

        self.generic_visit(node)

    def visit_While(self, node):
        if isinstance(node.test, ast.Constant) and not node.test.value:
            self.issues.append("Warning: Detected dead code in a 'while' statement with a constant False condition.")
        elif isinstance(node.test, (ast.Num, ast.Str, ast.NameConstant)) and not bool(
            node.test.n if isinstance(node.test, ast.Num) else
            node.test.s if isinstance(node.test, ast.Str) else
            node.test.value
        ):
            self.issues.append(
                "Warning: Detected dead code in a 'while' statement with a constant False-equivalent condition."
            )

        self.generic_visit(node)

    def visit_Exec(self, node):
        self.issues.append("Warning: Use of 'exec' detected. This can lead to security vulnerabilities.")
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in {'os', 'subprocess'}:
                self.issues.append(
                    f"Warning: Importing '{alias.name}' can lead to security risks if used improperly."
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in {'os', 'subprocess'}:
            self.issues.append(
                f"Warning: Importing from '{node.module}' can lead to security risks if used improperly."
            )
        self.generic_visit(node)

    def analyze(self, code):
        try:
            tree = ast.parse(code)
            self.visit(tree)
        except SyntaxError as e:
            self.issues.append(f"Syntax Error: {e}")
        return self.issues

def analyze_code_from_input():
    """(Optional) For interactive use—unchanged from your original code."""
    code = input("Enter your Python code:\n")
    analyzer = astParser()
    issues = analyzer.analyze(code)
    print("\nAnalysis Report:")
    for issue in issues:
        print(issue)

def analyze_code_from_file(filename):
    """(Optional) For interactive use—unchanged from your original code."""
    try:
        with open(filename, "r") as file:
            code = file.read()
        analyzer = astParser()
        issues = analyzer.analyze(code)
        print("\nAnalysis Report:")
        for issue in issues:
            print(issue)
    except FileNotFoundError:
        print("Error: File not found.")

if __name__ == "__main__":
    """
    This block adds a command-line interface so Jenkins (or any other CI system)
    can call this script and generate a JSON report.
    """
    import sys

    parser = argparse.ArgumentParser(description="AST Parser for analyzing Python code.")
    parser.add_argument("--file", help="Path to the Python file to analyze.")
    parser.add_argument("--output", help="Path to output JSON file.", default="ast_report.json")
    args = parser.parse_args()

    if not args.file:
        print("No file specified. Please use --file <path_to_file>.")
        sys.exit(1)

    try:
        with open(args.file, "r") as f:
            code = f.read()
        analyzer = astParser()
        issues = analyzer.analyze(code)

        with open(args.output, "w", encoding="utf-8") as out:
            json.dump(issues, out, indent=4)

        print(f"AST analysis completed. Results saved to {args.output}.")
    except FileNotFoundError:
        print("Error: File not found.")
        sys.exit(1)
