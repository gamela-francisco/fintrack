import csv
from app.models import Transaction

def save_transaction(transaction: Transaction) -> None:
    """
    Append a single transaction to the transactions.csv file.
    Creates the file with headers if it doesn't exist.
    """

    # Define the CSV filename
    filename = "transaction.csv"

    # Open the file in append mode so we add to the end without overwriting.
    #  newline='' prevents the extra blanklines on Windows
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)

        # if the file is empty, write the header row first
        if file.tell() == 0:
            writer.writerow(["amount", "description", "category", "date"])

        # write the transaction data as a row
        writer.writerow([
            transaction.amount,
            transaction.description,
            transaction.category,
            transaction.transaction_date.isoformat()]) # Convert date to YYYY-MM-DD string