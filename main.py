import ast
import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

def init_db():
    with sqlite3.connect("u.DB") as connect:
        cursor = connect.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solution REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        connect.commit()

init_db()

@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>ERROR: index.html not found!</h3>"

class AuctionItem(BaseModel):
    answer: str

# Safe evaluator using AST
def safe_eval(expr: str):
    allowed_operators = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.USub: lambda a: -a,
        ast.UAdd: lambda a: +a,
    }

    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
            return allowed_operators[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp) and type(node.op) in allowed_operators:
            return allowed_operators[type(node.op)](_eval(node.operand))
        else:
            raise ValueError("Unsupported or unsafe expression")

    node = ast.parse(expr, mode='eval')
    return _eval(node.body)

@app.post("/api/evaluate-bid")
def evaluate_bid(data: AuctionItem):
    try:
        raw_solution = float(safe_eval(data.answer))
        rounded_solution = round(raw_solution, 2)
        
        with sqlite3.connect("u.DB") as connect:
            cursor = connect.cursor()
            cursor.execute("INSERT INTO history (solution) VALUES (?)", (rounded_solution,))
            connect.commit()
        
        return {
            "status": "success",
            "raw": raw_solution,
            "round": rounded_solution
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": f"Invalid evaluation: {str(e)}"
        }
        #git add .
        #git commit -m "Add raw and rounded calculations"
        #git push origin main