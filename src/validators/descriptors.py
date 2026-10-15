"""
descriptors.py
Custom Python descriptors for validating attributes on data models.
I used descriptors here to satisfy the metaprogramming requirement from the assignment brief.
When an attribute is assigned, the descriptor validates the value automatically before saving it.
"""

from typing import Any, Pattern
from src.validators.exceptions import DataValidationError


class ValidatedAttribute:
    """
    Base descriptor class.
    Stores the attribute value inside the instance's __dict__ using a private name like '_price'.
    """
    def __set_name__(self, owner: Any, name: str) -> None:
        self.private_name = f"_{name}"
        self.public_name = name

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is None:
            return self
        return getattr(instance, self.private_name, None)


class PositiveNumber(ValidatedAttribute):
    """
    Validates that a number is greater than zero (or >= 0 if allow_zero=True).
    Used for price, duration, and CO2 emissions.
    """
    def __init__(self, allow_zero: bool = False):
        self.allow_zero = allow_zero

    def __set__(self, instance: Any, value: Any) -> None:
        try:
            num = float(value)
        except (ValueError, TypeError) as e:
            raise DataValidationError(f"Expected numeric value, got '{value}'", field=self.public_name) from e

        if self.allow_zero and num < 0:
            raise DataValidationError(f"Value must be >= 0, got {num}", field=self.public_name)
        elif not self.allow_zero and num <= 0:
            raise DataValidationError(f"Value must be strictly > 0, got {num}", field=self.public_name)

        setattr(instance, self.private_name, num)


class NonNegativeInt(ValidatedAttribute):
    """
    Validates that an integer is >= 0.
    Used for available seats and number of transfers.
    """
    def __set__(self, instance: Any, value: Any) -> None:
        try:
            val = int(value)
        except (ValueError, TypeError) as e:
            raise DataValidationError(f"Expected integer value, got '{value}'", field=self.public_name) from e

        if val < 0:
            raise DataValidationError(f"Value cannot be negative, got {val}", field=self.public_name)

        setattr(instance, self.private_name, val)


class BoundedFloat(ValidatedAttribute):
    """
    Validates that a float is between min_val and max_val.
    Used for customer rating (1.0 to 5.0).
    """
    def __init__(self, min_val: float, max_val: float):
        self.min_val = min_val
        self.max_val = max_val

    def __set__(self, instance: Any, value: Any) -> None:
        try:
            num = float(value)
        except (ValueError, TypeError) as e:
            raise DataValidationError(f"Expected numeric value, got '{value}'", field=self.public_name) from e

        if not (self.min_val <= num <= self.max_val):
            raise DataValidationError(
                f"Value must be between {self.min_val} and {self.max_val}, got {num}",
                field=self.public_name
            )

        setattr(instance, self.private_name, num)


class RegexValidatedString(ValidatedAttribute):
    """
    Validates that a string matches a regular expression pattern.
    Used for Offer IDs and Booking References.
    """
    def __init__(self, pattern: Pattern[str], description: str = "structured identifier"):
        self.pattern = pattern
        self.description = description

    def __set__(self, instance: Any, value: Any) -> None:
        if not isinstance(value, str):
            raise DataValidationError(
                f"Expected string for {self.description}, got {type(value).__name__}",
                field=self.public_name
            )

        cleaned = value.strip()
        if not self.pattern.match(cleaned):
            raise DataValidationError(
                f"Value '{cleaned}' does not match required {self.description} pattern '{self.pattern.pattern}'",
                field=self.public_name
            )
        setattr(instance, self.private_name, cleaned)
