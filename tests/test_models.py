import pytest
from app.models import Transaction

def test_valid_transaction():
    """
    Test creating a valid transaction with amount and description.
    """

    t = Transaction(amount = 25.50, description = "Lunch at cafe")

    assert t.amount == 25.50
    assert t.description == "Lunch at cafe"

def test_category_defaults_to_uncategorised():
    """
    Test that category defaults to 'Uncategorised' when not provided.
    """
    t = Transaction(amount = 25.50, description = "Lunch at cafe")
    assert t.category == "Uncategorised"