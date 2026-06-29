from datetime import date


class Transaction:
    def __init__(self, amount, description, category="Uncategorised", transaction_date=None):
        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number.")

        if amount == 0:
            raise ValueError("Amount cannot be zero")

        if not description or not description.strip():
            raise ValueError("Description cannot be empty.")

        self.amount = amount
        self.description = description
        self.category = category

        if transaction_date is None:
            self.transaction_date = date.today()
        else:
            self.transaction_date = transaction_date
