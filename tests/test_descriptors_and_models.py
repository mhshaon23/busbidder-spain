"""
Unit tests for data models, validation descriptors, and custom exceptions.
"""

import pytest
from src.models.offer import Offer
from src.models.request import TravellerRequest
from src.validators.exceptions import (
    DataValidationError,
    WeightValidationError,
    ConstraintViolationError,
)


def test_valid_offer_creation():
    offer = Offer(
        offer_id="OFF-CE-1001",
        company="Camino Express",
        origin="Madrid",
        destination="Barcelona",
        travel_date="2026-07-12",
        departure_time="08:30",
        arrival_time="13:30",
        duration_minutes=300,
        price=45.0,
        transfers=0,
        luggage_kg=20,
        is_changeable=True,
        is_refundable=True,
        available_seats=15,
        customer_rating=4.7,
        co2_kg_per_passenger=14.0,
    )
    assert offer.offer_id == "OFF-CE-1001"
    assert offer.price == 45.0
    assert offer.available_seats == 15
    assert offer.flexibility_score == 1.0


def test_negative_price_rejected():
    with pytest.raises(DataValidationError, match="Value must be strictly > 0"):
        Offer(
            offer_id="OFF-SR-1002",
            company="SolRuta",
            origin="Madrid",
            destination="Valencia",
            travel_date="2026-07-12",
            departure_time="08:00",
            arrival_time="12:00",
            duration_minutes=240,
            price=-10.0,  # Invalid
            transfers=0,
            luggage_kg=15,
            is_changeable=False,
            is_refundable=False,
            available_seats=20,
            customer_rating=4.0,
        )


def test_invalid_offer_id_regex_rejected():
    with pytest.raises(DataValidationError, match="Offer ID"):
        Offer(
            offer_id="BAD-ID-123",  # Does not match pattern r"^OFF-[A-Z]{2,4}-\d{4}$"
            company="SolRuta",
            origin="Madrid",
            destination="Valencia",
            travel_date="2026-07-12",
            departure_time="08:00",
            arrival_time="12:00",
            duration_minutes=240,
            price=25.0,
            transfers=0,
            luggage_kg=15,
            is_changeable=False,
            is_refundable=False,
            available_seats=20,
            customer_rating=4.0,
        )


def test_customer_rating_out_of_bounds_rejected():
    with pytest.raises(DataValidationError, match="between 1.0 and 5.0"):
        Offer(
            offer_id="OFF-VB-1003",
            company="VerdeBus",
            origin="Madrid",
            destination="Seville",
            travel_date="2026-07-12",
            departure_time="10:00",
            arrival_time="15:00",
            duration_minutes=300,
            price=35.0,
            transfers=0,
            luggage_kg=18,
            is_changeable=True,
            is_refundable=True,
            available_seats=20,
            customer_rating=6.5,  # Exceeds max 5.0
        )


def test_temporal_inconsistency_rejected():
    with pytest.raises(DataValidationError, match="Temporal inconsistency"):
        Offer(
            offer_id="OFF-CE-1004",
            company="Camino Express",
            origin="Madrid",
            destination="Toledo",
            travel_date="2026-07-12",
            departure_time="09:00",
            arrival_time="10:00",  # 60 mins journey
            duration_minutes=240,   # Claims 240 mins!
            price=15.0,
            transfers=0,
            luggage_kg=10,
            is_changeable=True,
            is_refundable=True,
            available_seats=20,
            customer_rating=4.5,
        )


def test_request_invalid_weights_rejected():
    with pytest.raises(WeightValidationError, match="Criteria weights must sum to 1.0"):
        TravellerRequest(
            destination="Malaga",
            date_from="2026-07-12",
            date_to="2026-07-14",
            weights={"price": 0.50, "duration": 0.20}  # Sum = 0.70 != 1.0
        )


def test_request_negative_weight_rejected():
    with pytest.raises(WeightValidationError, match="cannot be negative"):
        TravellerRequest(
            destination="Malaga",
            date_from="2026-07-12",
            date_to="2026-07-14",
            weights={"price": 1.20, "duration": -0.20}
        )


def test_request_reversed_dates_rejected():
    with pytest.raises(ConstraintViolationError, match="cannot precede start date"):
        TravellerRequest(
            destination="Malaga",
            date_from="2026-07-14",
            date_to="2026-07-12",  # End before start
        )

