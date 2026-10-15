"""
regex_patterns.py
Regular expression patterns used across BusBidder Spain.
Task 2 asks for regex where genuinely suitable:
- Booking reference: 'ES-' followed by 6 alphanumeric chars (e.g. ES-A4K891)
- Offer ID: 'OFF-' followed by company code and 4 digits (e.g. OFF-SR-1001)
- Time in 24h format (HH:MM)
- Date in ISO format (YYYY-MM-DD)
"""

import re

# 1. Booking Reference: ES- followed by 6 letters/digits
BOOKING_REF_PATTERN = re.compile(r"^ES-[A-Z0-9]{6}$")

# 2. Offer ID: OFF-COMPANY-NUMBER
OFFER_ID_PATTERN = re.compile(r"^OFF-[A-Z]{2,4}-\d{4}$")

# 3. 24h time format (00:00 to 23:59)
TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")

# 4. Standard ISO date format (YYYY-MM-DD)
DATE_PATTERN = re.compile(r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$")


def is_valid_booking_ref(ref: str) -> bool:
    """Helper to check if a booking reference is valid."""
    return bool(BOOKING_REF_PATTERN.match(ref.strip()))


def is_valid_offer_id(offer_id: str) -> bool:
    """Helper to check if an offer ID has the right format."""
    return bool(OFFER_ID_PATTERN.match(offer_id.strip()))


def is_valid_time(time_str: str) -> bool:
    """Helper to check if a time string is HH:MM."""
    return bool(TIME_PATTERN.match(time_str.strip()))


def is_valid_date(date_str: str) -> bool:
    """Helper to check if a date string is YYYY-MM-DD."""
    return bool(DATE_PATTERN.match(date_str.strip()))
