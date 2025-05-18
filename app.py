from flask import Flask, request, render_template
import ast
import os

app = Flask(__name__)

class CodeExplainer(ast.NodeVisitor):
    def __init__(self):
        self.explanations = []

    def visit_Assign(self, node):
        targets = [ast.unparse(t) for t in node.targets]
        value = ast.unparse(node.value)
        self.explanations.append(f"(Line {node.lineno}) Assigns {value} to {', '.join(targets)}.")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        args = [arg.arg for arg in node.args.args]
        self.explanations.append(f"(Line {node.lineno}) Defines a function '{node.name}' with arguments: {', '.join(args)}.")
        self.generic_visit(node)

    def visit_If(self, node):
        test = ast.unparse(node.test)
        self.explanations.append(f"(Line {node.lineno}) Checks the condition: '{test}'.")
        for stmt in node.body:
            self.visit(stmt)
        if node.orelse:
            self.explanations.append(f"(Line {node.orelse[0].lineno}) Executes the else block if the condition is False.")
            for stmt in node.orelse:
                self.visit(stmt)

    def visit_For(self, node):
        target = ast.unparse(node.target)
        iter_ = ast.unparse(node.iter)
        self.explanations.append(f"(Line {node.lineno}) Loops over '{iter_}' using variable '{target}'.")
        self.generic_visit(node)

    def visit_While(self, node):
        test = ast.unparse(node.test)
        self.explanations.append(f"(Line {node.lineno}) Runs a while loop with condition: '{test}'.")
        self.generic_visit(node)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            call_expr = ast.unparse(node.value)
            self.explanations.append(f"(Line {node.lineno}) Executes a function call: '{call_expr}'.")
        self.generic_visit(node)

    def visit_Return(self, node):
        value = ast.unparse(node.value) if node.value else 'nothing'
        self.explanations.append(f"(Line {node.lineno}) Returns {value}.")
        self.generic_visit(node)

    def explain(self, code):
        try:
            tree = ast.parse(code)
            self.visit(tree)
            return self.explanations
        except Exception as e:
            return [f"Error parsing code: {str(e)}"]

@app.route("/", methods=["GET", "POST"])
def index():
    explanation_output = ""
    code_input = ""

    if request.method == "POST":
        # Check if user uploaded a file
        if "file" in request.files and request.files["file"].filename != "":
            uploaded_file = request.files["file"]
            code_input = uploaded_file.read().decode("utf-8")
        else:
            # Or get code from textarea
            code_input = request.form.get("code", "")

        explainer = CodeExplainer()
        explanation_output = explainer.explain(code_input)

    return render_template("index.html", code=code_input, explanation=explanation_output)

if __name__ == "__main__":
    app.run(debug=True)
