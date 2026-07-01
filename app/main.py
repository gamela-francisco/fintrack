from fastapi import FastAPI
from typing import List
from app.schemas import TransactionBase
from app.storage import save_transaction, get_all_transactions

# Initialise the FastAPI application instance
app = FastAPI()

# We use this decorator to map HTTP GET requests sent to the root URL ("/")
# directly to the function defined immediately below it.
@app.get("/")
def read_root() -> dict:
    """
    Health check endpoint that returns a simple welcome message.

    This allows clients or deployment platforms to verify that the backend
    server is up and running correctly.
    """
    return {"message": "Welcome to FinTrack API"}

@app.post("/transactions")
def create_transaction(transaction: TransactionBase) -> dict:
    """
    Endpoint to log a new financial  transaction.

    1. Receives data matching the TransactionBase schema.
    2. The Pydantic 'bouncer' automatically validates it.
    3. Converts the valid schema object to a standard Python dictionary.
    4. Passes it to storage to be assigned an ID and saved.
    """
    # Convert Pydantic object to dictionary
    transaction_dict = transaction.model_dump()

    # Saving it using storage layer
    saved_record = save_transaction(transaction_dict)

    return saved_record

@app.get("/transactions")
def read_all_transactions() -> List[dict]:
    """
    Endpoint to retrieve all financial transactions.
    """
    return get_all_transactions()
