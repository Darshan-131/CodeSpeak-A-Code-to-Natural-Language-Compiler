from flask import Flask, request, render_template
import ast
import os

app = Flask(__name__)

class CodeExplainer(ast.NodeVisitor):
    def __init__(self):
        self.explanations = []

    def add_explanation(self, line, explanation, paragraph):
        self.explanations.append({
            "line": f"(Line {line}) {explanation}",
            "paragraph": paragraph
        })

    def visit_Assign(self, node):
        targets = [ast.unparse(t) for t in node.targets]
        value = ast.unparse(node.value)
        explanation = f"Assigns {value} to {', '.join(targets)}."
        paragraph = f"This line assigns the value '{value}' to the variable(s) '{', '.join(targets)}'."
        self.add_explanation(node.lineno, explanation, paragraph)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        args = [arg.arg for arg in node.args.args]
        explanation = f"Defines a function '{node.name}' with arguments: {', '.join(args)}."
        paragraph = f"The function '{node.name}' is created with parameters: {', '.join(args)}. It groups related code together."
        self.add_explanation(node.lineno, explanation, paragraph)
        self.generic_visit(node)

    def visit_If(self, node):
        test = ast.unparse(node.test)
        explanation = f"Checks the condition: '{test}'."
        paragraph = f"This line evaluates the condition '{test}' and decides which block of code to execute."
        self.add_explanation(node.lineno, explanation, paragraph)
        for stmt in node.body:
            self.visit(stmt)
        if node.orelse:
            explanation_else = f"Executes the else block if the condition is False."
            paragraph_else = f"If the condition is not met, this block will be executed."
            self.add_explanation(node.orelse[0].lineno, explanation_else, paragraph_else)
            for stmt in node.orelse:
                self.visit(stmt)

    def visit_For(self, node):
        target = ast.unparse(node.target)
        iter_ = ast.unparse(node.iter)
        explanation = f"Loops over '{iter_}' using variable '{target}'."
        paragraph = f"This line starts a for loop, iterating over '{iter_}' and using '{target}' for each item."
        self.add_explanation(node.lineno, explanation, paragraph)
        self.generic_visit(node)

    def visit_While(self, node):
        test = ast.unparse(node.test)
        explanation = f"Runs a while loop with condition: '{test}'."
        paragraph = f"This line creates a while loop that runs as long as the condition '{test}' is true."
        self.add_explanation(node.lineno, explanation, paragraph)
        self.generic_visit(node)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            call_expr = ast.unparse(node.value)
            explanation = f"Executes a function call: '{call_expr}'."
            paragraph = f"This line calls the function or method '{call_expr}' to perform an action."
            self.add_explanation(node.lineno, explanation, paragraph)
        self.generic_visit(node)

    def visit_Return(self, node):
        value = ast.unparse(node.value) if node.value else 'nothing'
        explanation = f"Returns {value}."
        paragraph = f"This line ends the function and returns the value '{value}' to the caller."
        self.add_explanation(node.lineno, explanation, paragraph)
        self.generic_visit(node)

    def explain(self, code):
        try:
            tree = ast.parse(code)
            self.visit(tree)
            return self.explanations
        except Exception as e:
            return [{"line": f"Error parsing code: {str(e)}", "paragraph": ""}]

@app.route("/", methods=["GET", "POST"])
def index():
    explanation_output = []
    code_input = ""

    if request.method == "POST":
        if "file" in request.files and request.files["file"].filename != "":
            uploaded_file = request.files["file"]
            code_input = uploaded_file.read().decode("utf-8")
        else:
            code_input = request.form.get("code", "")

        explainer = CodeExplainer()
        explanation_output = explainer.explain(code_input)

    return render_template("index.html", code=code_input, explanation=explanation_output)

if __name__ == "__main__":
    app.run(debug=True)
