from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field, field_validator


class TransactionBase(BaseModel):
    """
    Base Pydantic model for defining the schema and data types for
    a financial transaction.

    Ensures incoming request data contains the
    correct data types before reaching  business logic.
    """
    amount: Decimal = Field(...)
    description: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    date: date

    @field_validator('amount')
    @classmethod
    def prevent_zero_amount(cls, v: Decimal) -> Decimal:
        if v == 0:
            raise ValueError("Transaction amount cannot be exactly zero.")
        return v
