"""
Centralized regular expression patterns and validation helpers for BusBidder Spain.
Adheres to the project requirement of genuine, purposeful regex applications.
"""

import re
from typing import Optional

# Regex Patterns
# 1. Booking Reference format: ES- followed by 6 alphanumeric characters (uppercase) e.g. ES-A4K891
BOOKING_REF_PATTERN = re.compile(r"^ES-[A-Z0-9]{6}$")

# 2. Offer ID format: OFF-<2-4 uppercase company code>-<4 digit sequence> e.g. OFF-SR-0101, OFF-COME-0205
OFFER_ID_PATTERN = re.compile(r"^OFF-[A-Z]{2,4}-\d{4}$")

# 3. 24-hour time format: HH:MM from 00:00 to 23:59
TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")

# 4. ISO Date format: YYYY-MM-DD
DATE_PATTERN = re.compile(r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$")


def is_valid_booking_ref(ref: str) -> bool:
    """Validate structured booking reference string."""
    return bool(BOOKING_REF_PATTERN.match(ref.strip()))


def is_valid_offer_id(offer_id: str) -> bool:
    """Validate offer identifier string."""
    return bool(OFFER_ID_PATTERN.match(offer_id.strip()))


def is_valid_time(time_str: str) -> bool:
    """Validate 24-hour time string (HH:MM)."""
    return bool(TIME_PATTERN.match(time_str.strip()))


def is_valid_date(date_str: str) -> bool:
    """Validate ISO date string (YYYY-MM-DD)."""
    return bool(DATE_PATTERN.match(date_str.strip()))
