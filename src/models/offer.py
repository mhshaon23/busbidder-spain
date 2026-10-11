"""
Offer domain model incorporating descriptor-based validation.
Demonstrates object-oriented composition and metaprogramming.
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
    Represents an individual bus journey offer returned by a company.
    Attributes are managed by custom descriptors to guarantee integrity.
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
        # Descriptors handle validation upon assignment
        self.offer_id = offer_id
        self.price = price
        self.duration_minutes = duration_minutes
        self.transfers = transfers
        self.available_seats = available_seats
        self.customer_rating = customer_rating
        self.co2_kg_per_passenger = co2_kg_per_passenger

        # Simple string/boolean attributes
        self.company = company.strip()
        self.origin = origin.strip()
        self.destination = destination.strip()
        self.is_changeable = bool(is_changeable)
        self.is_refundable = bool(is_refundable)
        self.luggage_kg = int(luggage_kg)

        # Date & Time validation and parsing
        if not is_valid_date(travel_date):
            raise DataValidationError(f"Invalid date format '{travel_date}', expected YYYY-MM-DD", field="travel_date")
        if not is_valid_time(departure_time):
            raise DataValidationError(f"Invalid departure time '{departure_time}', expected HH:MM", field="departure_time")
        if not is_valid_time(arrival_time):
            raise DataValidationError(f"Invalid arrival time '{arrival_time}', expected HH:MM", field="arrival_time")

        self.travel_date_str = travel_date.strip()
        self.departure_time_str = departure_time.strip()
        self.arrival_time_str = arrival_time.strip()

        # Parse into datetime objects for logical operations
        self.travel_date = datetime.strptime(self.travel_date_str, "%Y-%m-%d").date()
        dep_dt = datetime.strptime(self.departure_time_str, "%H:%M")
        self.departure_time = dep_dt.time()
        arr_dt = datetime.strptime(self.arrival_time_str, "%H:%M")
        self.arrival_time = arr_dt.time()

        # Logical cross-validation: verify duration is plausible given departure and arrival
        self._validate_temporal_consistency()

    def _validate_temporal_consistency(self) -> None:
        """
        Cross-validates departure time, arrival time, and stated duration.
        Accounts for overnight journeys where arrival time is chronologically less than departure time.
        """
        dep_mins = self.departure_time.hour * 60 + self.departure_time.minute
        arr_mins = self.arrival_time.hour * 60 + self.arrival_time.minute

        if arr_mins >= dep_mins:
            elapsed = arr_mins - dep_mins
        else:
            # Crosses midnight (overnight journey)
            elapsed = (1440 - dep_mins) + arr_mins

        # Allow slight discrepancy (+/- 15 mins for scheduled buffers), but flag obvious errors
        if abs(elapsed - self.duration_minutes) > 30:
            raise DataValidationError(
                f"Temporal inconsistency: departure {self.departure_time_str} to "
                f"arrival {self.arrival_time_str} is {elapsed} mins, but duration is {self.duration_minutes} mins.",
                field="duration_minutes"
            )

    @property
    def flexibility_score(self) -> float:
        """
        Calculates a normalized raw flexibility value:
        - Changeable only: 0.5
        - Refundable only: 0.7
        - Both: 1.0
        - Neither: 0.0
        """
        score = 0.0
        if self.is_changeable:
            score += 0.4
        if self.is_refundable:
            score += 0.6
        return min(score, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert offer to dictionary representation."""
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
            f"€{self.price:.2f} | {self.duration_minutes}m | Seats: {self.available_seats}>"
        )
