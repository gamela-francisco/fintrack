from typing import List, Dict, Any

# This Python list acts as temporary, in-memory database table
TRANSACTIONS_DB: List[Dict[str, Any]] = []

def save_transaction(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates inserting a new transaction record into the database.
    Assigns an auto-incrementing ID to the record before saving.
    """

    # Auto-generate a simple ID based on the current length of the database
    new_id = len(TRANSACTIONS_DB) + 1

    # Create a copy of the dictionary and add to the ID key
    record = transaction_data.copy()
    record["id"] = new_id

    # Save the record into  in-memory list
    TRANSACTIONS_DB.append(record)
    return record


def get_all_transactions() -> List[Dict[str, Any]]:
    """
    Simulates a database query to select and fetch all transaction records.
    """
    return TRANSACTIONS_DB