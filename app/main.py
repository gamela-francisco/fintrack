from fastapi import FastAPI, HTTPException
from typing import List

from starlette.middleware.cors import CORSMiddleware

from app.schemas import TransactionBase

from contextlib import asynccontextmanager
from app.database import init_db
from app.database import get_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This block runs BEFORE the server starts accepting requests
    print("Initialising SQLite Database...")
    init_db()
    yield
    # Anything after the 'yield' would run when the server shuts down

# Pass the lifespan manager  into your FastAPI application
app = FastAPI(lifespan=lifespan)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows any website to make requests to this backend
    allow_credentials=True,
    allow_methods=["*"], # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"], # Allow any headers
)

@app.get("/transactions/summary")
def get_financial_summary() -> dict:
    """
    Executes high-performance SQL aggregation functions to compute
    Total Income, Total Expenses, and Net Balance directly on the hard drive
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query 1: Calculate Total Income (All positive numbers)
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE amount > 0;")
    income_row = cursor.fetchone()
    # defensive check - if database has no rows, default to 0.0
    total_income = income_row[0] if income_row[0] is not None else 0.0

    # Query 2: Calculate Total Expenses (All negative numbers)
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE amount < 0;")
    expense_row = cursor.fetchone()
    total_expenses = expense_row[0] if expense_row[0] is not None else 0.0

    conn.close()

    net_balance = total_income + total_expenses

    return {
        "total_income" : round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance": round(net_balance, 2)
    }



@app.get("/transactions")
def read_all_transactions() -> List[dict]:
    """
    Endpoint to retrieve all financial transactions from the SQLite database.
    """
    # Open connection pipe
    conn = get_db_connection()
    cursor = conn.cursor()

    # execute the SQL command to grab everything
    cursor.execute("SELECT * FROM transactions;")
    rows = cursor.fetchall()
    conn.close()

    # Convert the SQLite row objects into clean Python dictionaries
    # Because of conn.row_factory = sqlite3.Row, then we can loop through and do dict(row)
    transactions_list = [dict(row) for row in rows]

    return transactions_list

@app.post("/transactions")
def create_transaction(transaction: TransactionBase) -> dict:
    """
    Endpoint to log a new financial  transaction into the SQLite database.
    """
    # open connection pipe to the database file
    conn = get_db_connection()
    cursor = conn.cursor()

    safe_amount = float(transaction.amount)

    # execute the SQL command to insert our data rows securely
    cursor.execute("""
        INSERT INTO transactions (amount, description, category, date)
        VALUES (?, ?, ?, ?);
    """, (safe_amount, transaction.description, transaction.category, transaction.date))

    # commit saves the row, and cursor.lastrowid grabs the new ID assigned by SQLite
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    # return the exact saved record object back to the frontend
    return {
        "id": new_id,
        "amount": safe_amount,
        "description": transaction.description,
        "category": transaction.category,
        "date": transaction.date
    }

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int) -> dict:
    """
    Endpoint to permanently remove a financial transaction from the SQLite database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # execute the SQL delete command targeting the unique ID
    cursor.execute("DELETE FROM transactions WHERE id = ?;", (transaction_id,))

    conn.commit()
    conn.close()

    return {"message": f"Transaction {transaction_id} successfully deleted"}

@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, updated_tx: TransactionBase) -> dict:
    """
    Endpoint to modify an existing transaction's details inside the SQLite database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Step A: Check if the transaction actually exists first
    cursor.execute("SELECT id FROM transactions WHERE id = ?;", (transaction_id,))
    if cursor.fetchone() is None:
        conn.close()
        # FastAPI automatically handles HTTP exceptions elegantly
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Step B: Execute the SQL UPDATE command
    # We explicitly convert the Pydantic Decimal to a float to prevent driver binding errors
    cursor.execute(
        """
        UPDATE transactions 
        SET amount = ?, description = ?, category = ?, date = ?
        WHERE id = ?;
        """,
        (float(updated_tx.amount), updated_tx.description, updated_tx.category, updated_tx.date, transaction_id)
    )

    conn.commit()
    conn.close()

    return {"message": f"Transaction {transaction_id} successfully updated"}