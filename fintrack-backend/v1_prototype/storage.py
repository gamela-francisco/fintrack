import csv
from datetime import datetime
from v1_prototype import Transaction

def save_transaction(transaction: Transaction) -> None:
    """
    Append a single transaction to the transactions.csv file.
    Creates the file with headers if it doesn't exist.
    """

    # Define the CSV filename
    filename = "transactions.csv"

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


def load_transactions() -> list[Transaction]:
    """
    Read the CSV file and return a list of Transaction objects.
    Skips the header row. Returns an empty list if the file doesn't exist.
    """
    filename = "transactions.csv"
    transaction = []

    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)

            # Skip the header row
            # next(reader, None) consumes the first row and moves to the next data

            next(reader, None)

            for row in reader:
                # Each row is a list: [amount, description, category, date]
                amount = float(row[0])
                description = row[1]
                category = row[2]
                transaction_date = datetime.strptime(row[3], "%Y-%m-%d").date()

                # Create a Transaction object and add it to our list
                t = Transaction(
                    amount=amount,
                    description=description,
                    category=category,
                    transaction_date=transaction_date
                )
                transaction.append(t)

    except FileNotFoundError:
        pass

    return transaction