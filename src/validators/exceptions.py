"""
exceptions.py
Custom exceptions for the BusBidder Spain project (ACIT4420).
Defined specific exception classes so errors can be caught and handled cleanly.
"""


class BusBidderError(Exception):
    """Base exception for all errors in our BusBidder application."""
    pass


# -------------------------------------------------------------
# Data loading & validation errors
# -------------------------------------------------------------

class DataValidationError(BusBidderError):
    """Raised when a row in the dataset has invalid data (e.g. negative price)."""
    def __init__(self, message: str, row_identifier: str = "Unknown", field: str = "Unknown"):
        super().__init__(f"[{row_identifier}] Invalid field '{field}': {message}")
        self.row_identifier = row_identifier
        self.field = field


class CorruptRecordError(DataValidationError):
    """Raised when a row in the CSV is corrupted or missing required columns."""
    pass


class InvalidIdentifierError(DataValidationError):
    """Raised when an ID (like offer ID or booking reference) doesn't match the regex pattern."""
    pass


# -------------------------------------------------------------
# Filtering & Ranking errors
# -------------------------------------------------------------

class ConstraintViolationError(BusBidderError):
    """Raised when travel search dates or constraints are logically invalid."""
    pass


class RankingConfigurationError(BusBidderError):
    """Raised when ranking weights or criteria don't match what is supported."""
    pass


class WeightValidationError(RankingConfigurationError):
    """Raised when the user weights do not sum up to 1.0 (100%) or have negative values."""
    pass


# -------------------------------------------------------------
# Booking errors
# -------------------------------------------------------------

class BookingError(BusBidderError):
    """Base error for booking issues."""
    pass


class SeatUnavailableError(BookingError):
    """Raised when someone tries to book more seats than what's available."""
    pass


class InvalidBookingReferenceError(BookingError):
    """Raised when a booking reference format is wrong or not found."""
    pass
