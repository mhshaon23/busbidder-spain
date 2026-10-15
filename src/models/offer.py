"""
offer.py
Offer class representing a single bus journey offer.
Uses descriptors for attribute validation to ensure positive prices,
valid ratings (1-5), and proper ID formats.
"""

from datetime import datetime, time, date
from typing import Dict, Any
from src.validators.descriptors import (
    PositiveNumber,
    NonNegativeInt,
    BoundedFloat,
    RegexValidatedString,
)
from src.validators.regex_patterns import OFFER_ID_PATTERN, is_valid_time, is_valid_date
from src.validators.exceptions import DataValidationError


class Offer:
    """
    Represents one bus offer from a company.
    Attributes like price, seats, and rating are validated by descriptors.
    """
    offer_id = RegexValidatedString(OFFER_ID_PATTERN, "Offer ID")
    price = PositiveNumber()
    duration_minutes = PositiveNumber()
    transfers = NonNegativeInt()
    available_seats = NonNegativeInt()
    customer_rating = BoundedFloat(min_val=1.0, max_val=5.0)
    co2_kg_per_passenger = PositiveNumber(allow_zero=True)

    def __init__(
        self,
        offer_id: str,
        company: str,
        origin: str,
        destination: str,
        travel_date: str,
        departure_time: str,
        arrival_time: str,
        duration_minutes: int,
        price: float,
        transfers: int,
        luggage_kg: int,
        is_changeable: bool,
        is_refundable: bool,
        available_seats: int,
        customer_rating: float,
        co2_kg_per_passenger: float = 12.0,
    ):
        # Descriptors handle the validation automatically here:
        self.offer_id = offer_id
        self.price = price
        self.duration_minutes = duration_minutes
        self.transfers = transfers
        self.available_seats = available_seats
        self.customer_rating = customer_rating
        self.co2_kg_per_passenger = co2_kg_per_passenger

        # Basic string & boolean values
        self.company = company.strip()
        self.origin = origin.strip()
        self.destination = destination.strip()
        self.is_changeable = bool(is_changeable)
        self.is_refundable = bool(is_refundable)
        self.luggage_kg = int(luggage_kg)

        # Validate date and time strings using our regex helpers
        if not is_valid_date(travel_date):
            raise DataValidationError(f"Invalid date format '{travel_date}', expected YYYY-MM-DD", field="travel_date")
        if not is_valid_time(departure_time):
            raise DataValidationError(f"Invalid departure time '{departure_time}', expected HH:MM", field="departure_time")
        if not is_valid_time(arrival_time):
            raise DataValidationError(f"Invalid arrival time '{arrival_time}', expected HH:MM", field="arrival_time")

        self.travel_date_str = travel_date.strip()
        self.departure_time_str = departure_time.strip()
        self.arrival_time_str = arrival_time.strip()

        # Parse into datetime objects so we can do math/time checks
        self.travel_date = datetime.strptime(self.travel_date_str, "%Y-%m-%d").date()
        dep_dt = datetime.strptime(self.departure_time_str, "%H:%M")
        self.departure_time = dep_dt.time()
        arr_dt = datetime.strptime(self.arrival_time_str, "%H:%M")
        self.arrival_time = arr_dt.time()

        # Check that departure time, arrival time, and duration actually make sense together
        self._validate_temporal_consistency()

    def _validate_temporal_consistency(self) -> None:
        """
        Calculates travel minutes between departure and arrival to make sure
        it matches duration_minutes (with allowance for slight buffer).
        Also handles overnight trips (e.g. 23:00 to 05:00 next day).
        """
        dep_mins = self.departure_time.hour * 60 + self.departure_time.minute
        arr_mins = self.arrival_time.hour * 60 + self.arrival_time.minute

        if arr_mins >= dep_mins:
            elapsed = arr_mins - dep_mins
        else:
            # Trip crosses midnight
            elapsed = (1440 - dep_mins) + arr_mins

        # If there is a big difference between stated duration and elapsed time, raise error
        if abs(elapsed - self.duration_minutes) > 30:
            raise DataValidationError(
                f"Temporal inconsistency: departure {self.departure_time_str} to "
                f"arrival {self.arrival_time_str} is {elapsed} mins, but duration is {self.duration_minutes} mins.",
                field="duration_minutes"
            )

    @property
    def flexibility_score(self) -> float:
        """
        Simple score for ticket flexibility:
        - 0.4 points for changeable
        - 0.6 points for refundable
        Max score is 1.0 (both), 0.0 if neither.
        """
        score = 0.0
        if self.is_changeable:
            score += 0.4
        if self.is_refundable:
            score += 0.6
        return min(score, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert offer to dictionary (helpful for saving and printing tables)."""
        return {
            "offer_id": self.offer_id,
            "company": self.company,
            "origin": self.origin,
            "destination": self.destination,
            "travel_date": self.travel_date_str,
            "departure_time": self.departure_time_str,
            "arrival_time": self.arrival_time_str,
            "duration_minutes": self.duration_minutes,
            "price": self.price,
            "transfers": self.transfers,
            "luggage_kg": self.luggage_kg,
            "is_changeable": self.is_changeable,
            "is_refundable": self.is_refundable,
            "available_seats": self.available_seats,
            "customer_rating": self.customer_rating,
            "co2_kg_per_passenger": self.co2_kg_per_passenger,
        }

    def __repr__(self) -> str:
        return (
            f"<Offer {self.offer_id} | {self.company} -> {self.destination} | "
            f"EUR {self.price:.2f} | {self.duration_minutes}m | Seats: {self.available_seats}>"
        )
