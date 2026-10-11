"""
Booking manager handling capacity allocation, reference generation, and persistence.
"""

import json
import random
import string
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from src.models.offer import Offer
from src.models.booking import BookingRecord
from src.validators.exceptions import (
    SeatUnavailableError,
    InvalidBookingReferenceError,
    BookingError,
)
from src.validators.regex_patterns import is_valid_booking_ref
from src.loaders.logger import logger


class BookingManager:
    """
    Manages booking lifecycles, capacity inventory updates, and persistent state.
    """
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or (
            Path(__file__).resolve().parent.parent.parent / "data" / "bookings.json"
        )
        self.bookings: Dict[str, BookingRecord] = {}
        self._load_existing_bookings()

    def _load_existing_bookings(self) -> None:
        """Reads persisted bookings from JSON store."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                records = json.load(f)
            for item in records:
                rec = BookingRecord(
                    booking_reference=item["booking_reference"],
                    passenger_name=item["passenger_name"],
                    offer_id=item["offer_id"],
                    company=item["company"],
                    destination=item["destination"],
                    travel_date=item["travel_date"],
                    departure_time=item["departure_time"],
                    arrival_time=item["arrival_time"],
                    price_paid=item["price_paid"],
                    fare_conditions=item["fare_conditions"],
                    seats_booked=item.get("seats_booked", 1),
                    created_at=item.get("created_at"),
                    status=item.get("status", "CONFIRMED"),
                )
                self.bookings[rec.booking_reference] = rec
            logger.info(f"Loaded {len(self.bookings)} existing bookings from {self.storage_path}")
        except Exception as e:
            logger.error(f"Error loading bookings from {self.storage_path}: {e}")

    def _persist(self) -> None:
        """Serializes current bookings to storage file."""
        data = [b.to_dict() for b in self.bookings.values()]
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def generate_booking_reference(self) -> str:
        """
        Generates a unique reference guaranteed to conform to regex r"^ES-[A-Z0-9]{6}$".
        """
        characters = string.ascii_uppercase + string.digits
        while True:
            suffix = "".join(random.choices(characters, k=6))
            ref = f"ES-{suffix}"
            if is_valid_booking_ref(ref) and ref not in self.bookings:
                return ref

    def create_booking(self, offer: Offer, passenger_name: str, seats: int = 1) -> BookingRecord:
        """
        Books seats on a selected offer, decrements capacity consistently,
        and saves the transaction.
        """
        if offer.available_seats < seats:
            raise SeatUnavailableError(
                f"Cannot book {seats} seat(s) on offer {offer.offer_id}. "
                f"Only {offer.available_seats} remaining."
            )

        # Consistent inventory decrement
        offer.available_seats -= seats

        booking_ref = self.generate_booking_reference()
        fare_conditions = {
            "is_changeable": offer.is_changeable,
            "is_refundable": offer.is_refundable,
            "luggage_kg": offer.luggage_kg,
        }

        total_price = offer.price * seats

        record = BookingRecord(
            booking_reference=booking_ref,
            passenger_name=passenger_name,
            offer_id=offer.offer_id,
            company=offer.company,
            destination=offer.destination,
            travel_date=offer.travel_date_str,
            departure_time=offer.departure_time_str,
            arrival_time=offer.arrival_time_str,
            price_paid=total_price,
            fare_conditions=fare_conditions,
            seats_booked=seats,
            status="CONFIRMED"
        )

        self.bookings[booking_ref] = record
        self._persist()

        logger.info(
            f"Booking {booking_ref} confirmed for '{passenger_name}' on {offer.offer_id} "
            f"({offer.company} to {offer.destination}). Remaining seats: {offer.available_seats}"
        )
        return record

    def get_booking(self, reference: str) -> Optional[BookingRecord]:
        """Queries a booking by reference with regex validation."""
        cleaned_ref = reference.strip().upper()
        if not is_valid_booking_ref(cleaned_ref):
            raise InvalidBookingReferenceError(
                f"Reference '{reference}' does not match format 'ES-XXXXXX'."
            )
        return self.bookings.get(cleaned_ref)

    def cancel_booking(self, reference: str, offer: Optional[Offer] = None) -> bool:
        """
        Simulates booking cancellation. If fare conditions permit refund/change,
        marks status as CANCELLED and restores capacity.
        """
        record = self.get_booking(reference)
        if not record:
            return False

        if record.status == "CANCELLED":
            return False

        # Check fare conditions
        if not record.fare_conditions.get("is_refundable") and not record.fare_conditions.get("is_changeable"):
            raise BookingError(f"Booking {reference} has a strict non-refundable/non-changeable fare.")

        record.status = "CANCELLED"
        if offer and offer.offer_id == record.offer_id:
            offer.available_seats += record.seats_booked

        self._persist()
        logger.info(f"Booking {reference} cancelled. Capacity restored.")
        return True
