import ast
import sys


class astParser(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_FunctionDef(self, node):
        # Check for functions with empty bodies (potentially incomplete implementation)
        if isinstance(node.body[0], ast.Pass):
            self.issues.append(f"Warning: Function '{node.name}' has an empty body.")

        # Check for functions with arguments but no return statement
        if node.args.args and not any(isinstance(n, ast.Return) for n in ast.walk(node)):
            self.issues.append(f"Warning: Function '{node.name}' takes arguments but has no return statement.")

        self.generic_visit(node)

    def visit_If(self, node):
        # Detect dead code (if condition is a constant False, 0, None, or empty string)
        if isinstance(node.test, ast.Constant) and not node.test.value:
            self.issues.append("Warning: Detected dead code in an 'if' statement with a constant False condition.")
        # Support for older versions of Python
        elif isinstance(node.test, (ast.Num, ast.Str, ast.NameConstant)) and not bool(
                node.test.n if isinstance(node.test, ast.Num) else
                node.test.s if isinstance(node.test, ast.Str) else
                node.test.value
        ):
            self.issues.append(
                "Warning: Detected dead code in an 'if' statement with a constant False-equivalent condition.")

        # Continue visiting the rest of the AST (important for function bodies)
        self.generic_visit(node)

    def visit_While(self, node):
        # Detect dead code (if condition is a constant False, 0, None, or empty string)
        if isinstance(node.test, ast.Constant) and not node.test.value:
            self.issues.append("Warning: Detected dead code in an 'if' statement with a constant False condition.")
        # Support for older versions of Python
        elif isinstance(node.test, (ast.Num, ast.Str, ast.NameConstant)) and not bool(
                node.test.n if isinstance(node.test, ast.Num) else
                node.test.s if isinstance(node.test, ast.Str) else
                node.test.value
        ):
            self.issues.append(
                "Warning: Detected dead code in a 'while' statement with a constant False-equivalent condition.")

        # Continue visiting the rest of the AST (important for function bodies)
        self.generic_visit(node)

    def visit_Exec(self, node):
        # Detect use of exec (a potential security risk)
        self.issues.append("Warning: Use of 'exec' detected. This can lead to security vulnerabilities.")
        self.generic_visit(node)

    def visit_Import(self, node):
        # Detect potentially unsafe imports (e.g., os.system usage)
        for alias in node.names:
            if alias.name in {'os', 'subprocess'}:
                self.issues.append(f"Warning: Importing '{alias.name}' can lead to security risks if used improperly.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        # Similar check for 'from ... import ...'
        if node.module in {'os', 'subprocess'}:
            self.issues.append(
                f"Warning: Importing from '{node.module}' can lead to security risks if used improperly.")
        self.generic_visit(node)

    def analyze(self, code):
        try:
            tree = ast.parse(code)
            self.visit(tree)
        except SyntaxError as e:
            self.issues.append(f"Syntax Error: {e}")
        return self.issues


def analyze_code_from_input():
    code = input("Enter your Python code:\n")
    analyzer = astParser()
    issues = analyzer.analyze(code)
    print("\nAnalysis Report:")
    for issue in issues:
        print(issue)


def analyze_code_from_file(filename):
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
    if len(sys.argv) > 1:
        analyze_code_from_file(sys.argv[1])
    else:
        analyze_code_from_input()
