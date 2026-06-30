import os
import pytest
import csv
from app.models import Transaction
from app.storage import save_transaction
def test_save_transaction():
    """
    Test that saving a transaction writes it to the CSV file.
    """
    # 1. Create a transaction
    t = Transaction(amount = 100, description = "Test deposit")

    # 2. Save it
    save_transaction(t)

    # 3. Read the CSV file directly to verify it's there
    with open("transaction.csv") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # 4. Check that the row exists and has the correct data
    assert len(rows) == 2
    assert float(rows[1][0]) == 100
    assert rows[1][1] == "Test deposit"


