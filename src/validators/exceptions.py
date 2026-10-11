"""
Custom exception hierarchy for the BusBidder Spain platform.
Demonstrates structured error handling categorized by architectural domain.
"""

class BusBidderError(Exception):
    """Base exception for all domain-specific errors in BusBidder Spain."""
    pass


# ---------------------------------------------------------
# Data Ingestion & Validation Exceptions
# ---------------------------------------------------------

class DataValidationError(BusBidderError):
    """Raised when imported data fails schema or domain validation."""
    def __init__(self, message: str, row_identifier: str = "Unknown", field: str = "Unknown"):
        super().__init__(f"[{row_identifier}] Invalid field '{field}': {message}")
        self.row_identifier = row_identifier
        self.field = field


class CorruptRecordError(DataValidationError):
    """Raised when a data record is fundamentally malformed or missing key fields."""
    pass


class InvalidIdentifierError(DataValidationError):
    """Raised when structured IDs (Offer ID, Booking Ref) fail regex validation."""
    pass


# ---------------------------------------------------------
# Business Logic & Filtering Exceptions
# ---------------------------------------------------------

class ConstraintViolationError(BusBidderError):
    """Raised when an operation or query violates a hard travel constraint."""
    pass


class RankingConfigurationError(BusBidderError):
    """Raised when scoring criteria weights or parameters are invalid."""
    pass


class WeightValidationError(RankingConfigurationError):
    """Raised when ranking weights do not sum to 1.0 (or 100%) or contain negative weights."""
    pass


# ---------------------------------------------------------
# Booking & Inventory Exceptions
# ---------------------------------------------------------

class BookingError(BusBidderError):
    """Base exception for booking lifecycle failures."""
    pass


class SeatUnavailableError(BookingError):
    """Raised when attempting to book an offer with zero remaining capacity."""
    pass


class InvalidBookingReferenceError(BookingError):
    """Raised when querying or verifying a malformed booking reference."""
    pass
