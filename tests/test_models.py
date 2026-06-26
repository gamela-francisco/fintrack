import pytest
from datetime import date
from app.models import Transaction


def test_valid_transaction():
    """Test creating a valid transaction with all required fields."""
    t = Transaction(amount=25.50, description="Lunch at cafe")
    assert t.amount == 25.50
    assert t.description == "Lunch at cafe"
    assert t.category == "Uncategorized"  # Default category
    assert t.date == date.today()  # Default date
    assert t.is_income is True
    assert t.is_expense is False


def test_valid_negative_transaction():
    """Test creating a valid expense (negative amount)."""
    t = Transaction(amount=-10.00, description="Bus ticket", category="Transport")
    assert t.amount == -10.00
    assert t.category == "Transport"
    assert t.is_income is False
    assert t.is_expense is True


def test_zero_amount_raises_error():
    """Test that zero amount raises ValueError."""
    with pytest.raises(ValueError, match="Amount cannot be zero"):
        Transaction(amount=0, description="Free item")


def test_empty_description_raises_error():
    """Test that empty description raises ValueError."""
    with pytest.raises(ValueError, match="Description cannot be empty"):
        Transaction(amount=50, description="")

    with pytest.raises(ValueError, match="Description cannot be empty"):
        Transaction(amount=50, description="   ")  # Only whitespace


def test_non_numeric_amount_raises_error():
    """Test that non-numeric amount raises ValueError."""
    with pytest.raises(ValueError, match="Amount must be a number"):
        Transaction(amount="fifty", description="Invalid")


def test_custom_date():
    """Test passing a custom date."""
    custom_date = date(2025, 1, 15)
    t = Transaction(amount=100, description="Salary", category="Income", date=custom_date)
    assert t.date == custom_date