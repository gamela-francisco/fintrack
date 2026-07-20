import os
import csv
from v1_prototype import Transaction
from v1_prototype import save_transaction


def test_save_transaction():
    """
    Test that saving a transaction writes it to the CSV file.
    """

    # Start fresh. Delete the CSV file if it exists
    if os.path.exists("transactions.csv"):
        os.remove("transactions.csv")
    # 1. Create a transaction
    t = Transaction(amount = 100, description = "Test deposit")

    # 2. Save it
    save_transaction(t)

    # 3. Read the CSV file directly to verify it's there
    with open("transactions.csv") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # 4. Check that the row exists and has the correct data
    assert len(rows) == 2
    assert float(rows[1][0]) == 100
    assert rows[1][1] == "Test deposit"

def test_load_transactions():
    """
    Test that loading transactions reads the CSV and returns a list of Transaction objects.
    """

    # Start with the clean slate
    if os.path.exists("transactions.csv"):
        os.remove("transactions.csv")

    # Create and save two transactions
    t1 = Transaction(amount = -50, description = "Groceries", category = "Food")
    t2 = Transaction(amount = 200, description = "Salary", category = "Income")
    save_transaction(t1)
    save_transaction(t2)

    # Load them back
    from v1_prototype import load_transactions
    transactions = load_transactions()

    assert len(transactions) == 2
    assert transactions[0].amount == -50.0
    assert transactions[0].description == "Groceries"
    assert transactions[0].category == "Food"

    assert transactions[1].amount == 200.0
    assert transactions[1].description == "Salary"
    assert transactions[1].category == "Income"

    if os.path.exists("transactions.csv"):
        os.remove("transactions.csv")
