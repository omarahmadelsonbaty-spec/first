from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3

# 1. Initialize FastAPI engine
app = FastAPI()

# Helper function to initialize the DB if it doesn't exist
def init_db():
    with sqlite3.connect("u.DB") as connect:
        cursor = connect.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solution REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        connect.commit()

# Run initialization on startup
init_db()

# Serve the HTML interface at the root and index path
@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>ERROR: index.html not found in the AI_Startup folder!</h3>"

# 3. Pydantic validation contract
class AuctionItem(BaseModel):
    answer: str

# 4. Evaluation endpoint with thread-safe database logging
@app.post("/api/evaluate-bid")
def evaluate_bid(data: AuctionItem):
    try:
        raw_solution = float(eval(data.answer, {"__builtins__": None}, {}))
        rounded_solution = round(raw_solution, 2)
        
        # Open a connection specific to THIS thread and request
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
        git add .
        git commit -m "Add raw and rounded calculations"
        git push origin main