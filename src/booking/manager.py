"""
manager.py
Simulates booking a ticket on an offer.
Tasks handled:
- Checks if seats are available
- Reduces the seats on the offer
- Generates a unique booking reference matching regex 'ES-[A-Z0-9]{6}'
- Saves the booking record to data/bookings.json
- Generates a formatted text confirmation ticket
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
    Manages booking tickets, saving them to JSON, and decrementing available seats.
    """
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or (
            Path(__file__).resolve().parent.parent.parent / "data" / "bookings.json"
        )
        self.bookings: Dict[str, BookingRecord] = {}
        self._load_existing_bookings()

    def _load_existing_bookings(self) -> None:
        """Loads previously saved bookings from data/bookings.json if the file exists."""
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
            logger.error(f"Error reading bookings from {self.storage_path}: {e}")

    def apply_existing_bookings(self, offers: List[Offer]) -> int:
        """
        Re-applies saved CONFIRMED bookings to freshly loaded offers.
        offers.csv stays the original catalogue and bookings.json is the ledger,
        so the real capacity is: catalogue seats - seats in confirmed bookings.
        Without this, seats would reset to full every time the program restarts.
        Returns the number of seats deducted.
        """
        offers_by_id = {o.offer_id: o for o in offers}
        deducted = 0
        for rec in self.bookings.values():
            if rec.status != "CONFIRMED":
                continue
            offer = offers_by_id.get(rec.offer_id)
            if offer is None:
                logger.warning(f"Booking {rec.booking_reference} refers to unknown offer {rec.offer_id}")
                continue
            # Never go below zero, even if the ledger was edited by hand
            seats = min(rec.seats_booked, offer.available_seats)
            offer.available_seats -= seats
            deducted += seats
        logger.info(f"Applied {deducted} booked seat(s) from {self.storage_path.name} to the offer catalogue")
        return deducted

    def _persist(self) -> None:
        """Helper to save the current bookings dictionary to JSON."""
        data = [b.to_dict() for b in self.bookings.values()]
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def generate_booking_reference(self) -> str:
        """
        Generates a unique booking code matching the regex: r'^ES-[A-Z0-9]{6}$'.
        Example: ES-A4K891
        """
        chars = string.ascii_uppercase + string.digits
        while True:
            code = "".join(random.choices(chars, k=6))
            ref = f"ES-{code}"
            # Ensure it is valid regex and not already used
            if is_valid_booking_ref(ref) and ref not in self.bookings:
                return ref

    def create_booking(self, offer: Offer, passenger_name: str, seats: int = 1) -> BookingRecord:
        """
        Books seats on the offer:
        1. Checks capacity
        2. Deducts available seats from the offer
        3. Creates and saves a BookingRecord
        """
        if offer.available_seats < seats:
            raise SeatUnavailableError(
                f"Cannot book {seats} seat(s) on offer {offer.offer_id}. "
                f"Only {offer.available_seats} seat(s) left."
            )

        # Deduct available seats
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
            f"Booking {booking_ref} created for {passenger_name} ({offer.offer_id}). "
            f"Remaining seats on offer: {offer.available_seats}"
        )
        return record

    def get_booking(self, reference: str) -> Optional[BookingRecord]:
        """Finds a booking by its reference code (validating the code first)."""
        cleaned_ref = reference.strip().upper()
        if not is_valid_booking_ref(cleaned_ref):
            raise InvalidBookingReferenceError(
                f"Reference '{reference}' does not match format 'ES-XXXXXX'."
            )
        return self.bookings.get(cleaned_ref)

    def cancel_booking(self, reference: str, offer: Optional[Offer] = None) -> bool:
        """
        Cancels a booking if fare conditions allow it, and restores seat capacity.
        """
        record = self.get_booking(reference)
        if not record:
            return False

        if record.status == "CANCELLED":
            return False

        # Check if the ticket can be refunded or changed
        if not record.fare_conditions.get("is_refundable") and not record.fare_conditions.get("is_changeable"):
            raise BookingError(f"Booking {reference} has a non-refundable/non-changeable fare.")

        record.status = "CANCELLED"
        if offer and offer.offer_id == record.offer_id:
            offer.available_seats += record.seats_booked

        self._persist()
        logger.info(f"Booking {reference} cancelled. Seat capacity restored.")
        return True
