from fastapi import FastAPI, HTTPException
from typing import List, Optional
from starlette.middleware.cors import CORSMiddleware
from decimal import Decimal
from app.schemas import TransactionBase

from contextlib import asynccontextmanager
from app.database import init_db
from app.database import get_db_connection

from app.categorizer import OllamaCategorizer
categorizer = OllamaCategorizer()

import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This block runs BEFORE the server starts accepting requests
    print("Initialising PostgreSQL Database...")
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
    Total Income, Total Expenses, and Net Balance directly in the database
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query 1: Calculate Total Income (All positive numbers)
    cursor.execute("SELECT SUM(amount) as total FROM transactions WHERE amount > 0;")
    income_row = cursor.fetchone()
    # defensive check - if database has no rows, default to 0.0
    total_income = income_row["total"] if income_row["total"] is not None else Decimal("0.00")

    # Query 2: Calculate Total Expenses (All negative numbers)
    cursor.execute("SELECT SUM(amount) as total FROM transactions WHERE amount < 0;")
    expense_row = cursor.fetchone()
    total_expenses = expense_row["total"] if expense_row["total"] is not None else Decimal("0.00")

    conn.close()

    net_balance = total_income + total_expenses

    return {
        "total_income" : round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance": round(net_balance, 2)
    }



@app.get("/transactions")
def read_all_transactions(search: Optional[str] = None, category: Optional[str] = None) -> List[dict]:
    """
    Retrieves transactions from the database, equipped with dynamic,
    case-insensitive search pattern matching and category filtering.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # The '1=1' base trick allows us to cleanly append dynamic filters
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    # If the user typed something into the search bar
    if search:
        query += " AND LOWER(description) LIKE LOWER(%s)"
        params.append(f"%{search}%")  # The '%' wildcards mean "contains this text"

    # If the user selected or passed a specific category filter
    if category:
        query += " AND LOWER(category) = LOWER(%s)"
        params.append(category)

    query += ";"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@app.post("/transactions")
def create_transaction(transaction: TransactionBase) -> dict:
    """
    Endpoint to log a new financial  transaction into the PostgreSQL database.
    """
    # open connection to the PostgreSQL database
    conn = get_db_connection()
    cursor = conn.cursor()




    # execute the SQL command to insert our data rows securely
    cursor.execute("""
        INSERT INTO transactions (amount, description, category, date)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (transaction.amount, transaction.description, transaction.category, transaction.date))


    new_id = cursor.fetchone()["id"]
    conn.commit()
    conn.close()

    # return the exact saved record object back to the frontend
    return {
        "id": new_id,
        "amount": transaction.amount,
        "description": transaction.description,
        "category": transaction.category,
        "date": transaction.date
    }

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int) -> dict:
    """
    Endpoint to permanently remove a financial transaction from the PostgreSQL database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # check if the transaction exists first
    cursor.execute("SELECT id from transactions WHERE id = %s", (transaction_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")

    # execute the SQL delete command targeting the unique ID
    cursor.execute("DELETE FROM transactions WHERE id = %s;", (transaction_id,))

    conn.commit()
    conn.close()

    return {"message": f"Transaction {transaction_id} successfully deleted"}

@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, updated_tx: TransactionBase) -> dict:
    """
    Endpoint to modify an existing transaction's details inside the PostgreSQL database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Step A: Check if the transaction actually exists first
    cursor.execute("SELECT id FROM transactions WHERE id = %s;", (transaction_id,))
    if cursor.fetchone() is None:
        conn.close()
        # FastAPI automatically handles HTTP exceptions elegantly
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Step B: Execute the SQL UPDATE command
    cursor.execute(
        """
        UPDATE transactions 
        SET amount = %s, description = %s, category = %s, date = %s
        WHERE id = %s;
        """,
        (updated_tx.amount, updated_tx.description, updated_tx.category, updated_tx.date, transaction_id)
    )

    conn.commit()
    conn.close()

    return {"message": f"Transaction {transaction_id} successfully updated"}

@app.post("/transactions/{transaction_id}/categorize")
async def categorize_transaction(transaction_id: int) -> dict:
    conn = get_db_connection()

    # Open connection
    try:
        cursor = conn.cursor()
        # fetch one row
        cursor.execute(
            "SELECT * FROM transactions WHERE id = %s", (transaction_id,)
        )
        row = cursor.fetchone()
        # if not found -> raise
        if row is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        try:
            category = await categorizer.categorize(row["description"])
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise HTTPException(status_code=502, detail="AI service unavailable")

        cursor.execute("UPDATE transactions SET category = %s WHERE id = %s", (category, transaction_id))
        cursor.execute("SELECT * FROM transactions where id = %s", (transaction_id,))
        updated_row = cursor.fetchone()

        conn.commit()
        return dict(updated_row)
    finally:
        conn.close()