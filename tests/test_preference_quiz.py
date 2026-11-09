"""
Unit tests for the optional preference elicitation quiz module.
"""

import pytest
from src.extensions.preference_quiz import calculate_weights_from_ratings
from src.models.request import TravellerRequest


def test_calculate_weights_sum_to_one():
    ratings = {
        "price": 5,
        "duration": 4,
        "departure_time": 3,
        "flexibility": 2,
        "eco_score": 1,
    }
    weights = calculate_weights_from_ratings(ratings)

    # Must sum to 1.0
    assert sum(weights.values()) == pytest.approx(1.0, abs=1e-4)
    # Price should have the highest weight
    assert max(weights, key=weights.get) == "price"
    # Eco should have the lowest weight
    assert min(weights, key=weights.get) == "eco_score"


def test_equal_ratings_produce_equal_weights():
    # If the user answered 4 to all questions (the 'I want everything' trap)
    ratings = {
        "price": 4,
        "duration": 4,
        "departure_time": 4,
        "flexibility": 4,
        "eco_score": 4,
    }
    weights = calculate_weights_from_ratings(ratings)

    assert sum(weights.values()) == pytest.approx(1.0, abs=1e-4)
    for w in weights.values():
        assert w == pytest.approx(0.20, abs=1e-3)


def test_weights_work_with_traveller_request():
    ratings = {
        "price": 5,
        "duration": 2,
        "departure_time": 3,
        "flexibility": 1,
    }
    weights = calculate_weights_from_ratings(ratings)

    # Check that TravellerRequest accepts these weights without raising WeightValidationError
    req = TravellerRequest(
        destination="Malaga",
        date_from="2026-07-12",
        date_to="2026-07-14",
        weights=weights
    )
    assert req.weights["price"] > req.weights["duration"]
