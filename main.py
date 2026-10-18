from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3

# 1. Initialize SQLite database connection
connect = sqlite3.connect("u.DB", check_same_thread=False)
cursor = connect.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS history (
    e_id INTEGER PRIMARY KEY
    solution REAL
    created_at DEFAULT TIMESTAMP
)''')
connect.commit()

# 2. Initialize FastAPI engine
app = FastAPI()

# Catch BOTH the root and the explicit file request
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

# 4. Serve the HTML interface directly at the root address (http://127.0.0.1:5500/)
@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>ERROR: index.html not found in the AI_Startup folder!</h3>"

@app.post("/api/evaluate-bid")
def evaluate_bid(data: AuctionItem):
    try:
        # Safely evaluate math expression
        raw_solution = float(eval(data.answer, {"__builtins__": None}, {}))
        rounded_solution = round(raw_solution, 2)
        
        cursor.execute("INSERT INTO history VALUES ((?))", (rounded_solution))
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