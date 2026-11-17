"""
Unit tests for simulated booking management, capacity allocation, and cancellation.
"""

from pathlib import Path
import pytest
from src.booking.manager import BookingManager
from src.models.offer import Offer
from src.validators.exceptions import (
    SeatUnavailableError,
    InvalidBookingReferenceError,
    BookingError,
)


@pytest.fixture
def test_offer():
    return Offer(
        offer_id="OFF-CE-2001",
        company="Camino Express",
        origin="Madrid",
        destination="Cordoba",
        travel_date="2026-07-13",
        departure_time="09:00",
        arrival_time="12:00",
        duration_minutes=180,
        price=35.0,
        transfers=0,
        luggage_kg=20,
        is_changeable=True,
        is_refundable=True,
        available_seats=3,
        customer_rating=4.7,
        co2_kg_per_passenger=10.0,
    )


def test_successful_booking_lifecycle(tmp_path, test_offer):
    storage_path = tmp_path / "test_bookings.json"
    manager = BookingManager(storage_path=storage_path)

    initial_seats = test_offer.available_seats
    record = manager.create_booking(test_offer, passenger_name="Carlos Ruiz", seats=2)

    # 1. Capacity was reduced consistently
    assert test_offer.available_seats == initial_seats - 2
    # 2. Valid booking reference format
    assert record.booking_reference.startswith("ES-")
    assert len(record.booking_reference) == 9
    assert record.seats_booked == 2
    assert record.price_paid == 70.0

    # 3. Persistence verification
    assert storage_path.exists()
    retrieved = manager.get_booking(record.booking_reference)
    assert retrieved is not None
    assert retrieved.passenger_name == "Carlos Ruiz"

    # 4. Ticket string generation
    ticket = record.generate_ticket()
    assert "BUSBIDDER SPAIN TICKET" in ticket
    assert record.booking_reference in ticket


def test_seat_exhaustion_raises(tmp_path, test_offer):
    storage_path = tmp_path / "test_bookings.json"
    manager = BookingManager(storage_path=storage_path)

    # Attempting to book 4 seats when only 3 are available
    with pytest.raises(SeatUnavailableError):
        manager.create_booking(test_offer, passenger_name="Group Booking", seats=4)


def test_invalid_reference_format_raises(tmp_path):
    storage_path = tmp_path / "test_bookings.json"
    manager = BookingManager(storage_path=storage_path)

    with pytest.raises(InvalidBookingReferenceError):
        manager.get_booking("INVALID-REF-99")


def test_cancellation_and_seat_restoration(tmp_path, test_offer):
    storage_path = tmp_path / "test_bookings.json"
    manager = BookingManager(storage_path=storage_path)

    record = manager.create_booking(test_offer, passenger_name="Ana Lopez", seats=1)
    assert test_offer.available_seats == 2

    # Cancel booking
    success = manager.cancel_booking(record.booking_reference, offer=test_offer)
    assert success is True
    assert record.status == "CANCELLED"
    # Seats restored
    assert test_offer.available_seats == 3



def test_bookings_reduce_capacity_after_restart(tmp_path, test_offer):
    storage_path = tmp_path / "test_bookings.json"
    manager = BookingManager(storage_path=storage_path)
    manager.create_booking(test_offer, passenger_name="Ana Lopez", seats=2)

    # Simulate a program restart: the offer is reloaded from the catalogue with full capacity
    reloaded_offer = Offer(**{**test_offer.to_dict(), "available_seats": 3})
    restarted_manager = BookingManager(storage_path=storage_path)
    deducted = restarted_manager.apply_existing_bookings([reloaded_offer])

    assert deducted == 2
    assert reloaded_offer.available_seats == 1


def test_cancelled_bookings_do_not_reduce_capacity_after_restart(tmp_path, test_offer):
    storage_path = tmp_path / "test_bookings.json"
    manager = BookingManager(storage_path=storage_path)
    record = manager.create_booking(test_offer, passenger_name="Ana Lopez", seats=1)
    manager.cancel_booking(record.booking_reference, offer=test_offer)

    reloaded_offer = Offer(**{**test_offer.to_dict(), "available_seats": 3})
    restarted_manager = BookingManager(storage_path=storage_path)
    restarted_manager.apply_existing_bookings([reloaded_offer])

    assert reloaded_offer.available_seats == 3


def _offer_with_fare(test_offer, changeable, refundable):
    return Offer(**{**test_offer.to_dict(), "is_changeable": changeable, "is_refundable": refundable})


def test_refundable_fare_gets_full_refund(tmp_path, test_offer):
    manager = BookingManager(storage_path=tmp_path / "b.json")
    record = manager.create_booking(test_offer, passenger_name="Ana Lopez", seats=2)  # EUR 70.00

    manager.cancel_booking(record.booking_reference, offer=test_offer)
    assert record.cancellation_fee == 0.0
    assert record.refund_amount == 70.0


def test_changeable_only_fare_pays_cancellation_fee(tmp_path, test_offer):
    offer = _offer_with_fare(test_offer, changeable=True, refundable=False)
    manager = BookingManager(storage_path=tmp_path / "b.json")
    record = manager.create_booking(offer, passenger_name="Ana Lopez", seats=2)  # EUR 70.00

    manager.cancel_booking(record.booking_reference, offer=offer)
    assert record.cancellation_fee == 17.5   # 25% fee
    assert record.refund_amount == 52.5
    assert "Refund (simulated): EUR 52.50" in record.generate_ticket()


def test_rigid_fare_cannot_be_cancelled(tmp_path, test_offer):
    offer = _offer_with_fare(test_offer, changeable=False, refundable=False)
    manager = BookingManager(storage_path=tmp_path / "b.json")
    record = manager.create_booking(offer, passenger_name="Ana Lopez", seats=1)

    with pytest.raises(BookingError):
        manager.cancel_booking(record.booking_reference, offer=offer)
    assert record.status == "CONFIRMED"
    assert offer.available_seats == 2


def test_refund_is_saved_and_reloaded(tmp_path, test_offer):
    offer = _offer_with_fare(test_offer, changeable=True, refundable=False)
    storage_path = tmp_path / "b.json"
    manager = BookingManager(storage_path=storage_path)
    record = manager.create_booking(offer, passenger_name="Ana Lopez", seats=1)  # EUR 35.00
    manager.cancel_booking(record.booking_reference)

    reloaded = BookingManager(storage_path=storage_path).get_booking(record.booking_reference)
    assert reloaded.status == "CANCELLED"
    assert reloaded.cancellation_fee == 8.75 and reloaded.refund_amount == 26.25
    assert reloaded.cancelled_at is not None
