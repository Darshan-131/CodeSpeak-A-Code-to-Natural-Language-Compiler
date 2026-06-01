from flask import Flask, request, render_template
from dotenv import load_dotenv

import ast
import os

app = Flask(__name__)

class ASTSummaryVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.variables = []
        self.loops = []
        self.conditions = []

    def visit_FunctionDef(self, node):
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append(target.id)
        self.generic_visit(node)

    def visit_For(self, node):
        self.loops.append("for loop")
        self.generic_visit(node)

    def visit_While(self, node):
        self.loops.append("while loop")
        self.generic_visit(node)

    def visit_If(self, node):
        self.conditions.append("if statement")
        self.generic_visit(node)

def extract_summary(code):
    tree = ast.parse(code)

    visitor = ASTSummaryVisitor()
    visitor.visit(tree)

    return {
        "functions": visitor.functions,
        "variables": visitor.variables,
        "loops": visitor.loops,
        "conditions": visitor.conditions
    }

import google.generativeai as genai


load_dotenv(dotenv_path=".env")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_explanation(code):

    summary = extract_summary(code)

    prompt = f"""
    You are a code explanation assistant.

    Code:
    {code}

    AST Summary:
    {summary}

    Provide a concise explanation using the following format:

    1. Purpose (2-3 lines)
    2. Important Functions
    3. Important Variables
    4. Logic Flow (4-5 bullet points)
    5. Time Complexity
    6. Space Complexity

    Keep the explanation under 250 words.
    Avoid teaching basic programming concepts unless necessary.
    """

    response = model.generate_content(prompt)
    

    return response.text

@app.route("/", methods=["GET", "POST"])
def index():
    explanation_o= []
    code_input = ""

    if request.method == "POST":
        if "file" in request.files and request.files["file"].filename != "":
            uploaded_file = request.files["file"]
            code_input = uploaded_file.read().decode("utf-8")
        else:
            code_input = request.form.get("code", "")

        explanation_o = generate_explanation(code_input)

    return render_template("index.html", code=code_input, explanation=explanation_o)

if __name__ == "__main__":
    app.run(debug=True)
