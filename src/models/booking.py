"""
Booking entity and representation models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
from src.validators.descriptors import RegexValidatedString
from src.validators.regex_patterns import BOOKING_REF_PATTERN


class BookingRecord:
    """
    Immutable representation of a confirmed booking transaction.
    Uses regex descriptor to ensure booking reference matches 'ES-[A-Z0-9]{6}'.
    """
    booking_reference = RegexValidatedString(BOOKING_REF_PATTERN, "Booking Reference")

    def __init__(
        self,
        booking_reference: str,
        passenger_name: str,
        offer_id: str,
        company: str,
        destination: str,
        travel_date: str,
        departure_time: str,
        arrival_time: str,
        price_paid: float,
        fare_conditions: Dict[str, Any],
        seats_booked: int = 1,
        created_at: str = None,
        status: str = "CONFIRMED",
    ):
        self.booking_reference = booking_reference
        self.passenger_name = passenger_name.strip()
        self.offer_id = offer_id.strip()
        self.company = company.strip()
        self.destination = destination.strip()
        self.travel_date = travel_date.strip()
        self.departure_time = departure_time.strip()
        self.arrival_time = arrival_time.strip()
        self.price_paid = float(price_paid)
        self.fare_conditions = fare_conditions
        self.seats_booked = seats_booked
        self.created_at = created_at or datetime.now().isoformat()
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert booking to serializable dictionary."""
        return {
            "booking_reference": self.booking_reference,
            "passenger_name": self.passenger_name,
            "offer_id": self.offer_id,
            "company": self.company,
            "destination": self.destination,
            "travel_date": self.travel_date,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "price_paid": self.price_paid,
            "fare_conditions": self.fare_conditions,
            "seats_booked": self.seats_booked,
            "created_at": self.created_at,
            "status": self.status,
        }

    def generate_ticket(self) -> str:
        """Generates a formatted text ticket for output presentation."""
        return (
            "========================================================\n"
            "                 BUSBIDDER SPAIN TICKET                 \n"
            "========================================================\n"
            f" Booking Reference : {self.booking_reference}\n"
            f" Status            : {self.status}\n"
            f" Passenger Name    : {self.passenger_name}\n"
            f" Operator          : {self.company}\n"
            f" Route             : Madrid -> {self.destination}\n"
            f" Travel Date       : {self.travel_date}\n"
            f" Schedule          : {self.departure_time} - {self.arrival_time}\n"
            f" Seats Booked      : {self.seats_booked}\n"
            f" Total Paid        : EUR {self.price_paid:.2f}\n"
            "--------------------------------------------------------\n"
            " Fare Conditions:\n"
            f"  - Changeable     : {'Yes' if self.fare_conditions.get('is_changeable') else 'No'}\n"
            f"  - Refundable     : {'Yes' if self.fare_conditions.get('is_refundable') else 'No'}\n"
            f"  - Luggage Limit  : {self.fare_conditions.get('luggage_kg', 0)} kg included\n"
            "========================================================"
        )

