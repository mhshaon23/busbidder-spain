"""
Unit tests for ranking engine, normalization math, criteria registry, and explainability.
"""

import pytest
from src.engine.normalizers import (
    normalize_cost_criterion,
    normalize_benefit_criterion,
    normalize_departure_convenience,
)
from src.engine.criteria import CRITERIA_REGISTRY
from src.engine.ranker import RankingEngine
from src.engine.explainer import RecommendationExplainer
from src.models.offer import Offer
from src.models.request import TravellerRequest


def test_cost_normalization_lower_is_better():
    values = [20.0, 50.0, 100.0]
    # Lowest (20.0) should get 100.0
    assert normalize_cost_criterion(values, 20.0) == 100.0
    # Highest (100.0) should get 0.0
    assert normalize_cost_criterion(values, 100.0) == 0.0
    # Midpoint
    assert normalize_cost_criterion(values, 60.0) == 50.0


def test_benefit_normalization_higher_is_better():
    values = [1.0, 3.0, 5.0]
    # Highest (5.0) should get 100.0
    assert normalize_benefit_criterion(values, 5.0) == 100.0
    # Lowest (1.0) should get 0.0
    assert normalize_benefit_criterion(values, 1.0) == 0.0


def test_normalization_single_value_edge_case():
    # If all offers have identical value, all should receive full 100.0
    values = [42.0, 42.0]
    assert normalize_cost_criterion(values, 42.0) == 100.0
    assert normalize_benefit_criterion(values, 42.0) == 100.0


def test_circular_departure_time_convenience():
    # Target: 09:00
    # Departure: 09:00 -> delta = 0 -> score 100.0
    assert normalize_departure_convenience(9.0, 9.0) == 100.0
    # Departure: 13:00 -> delta = 4 hours -> score 50.0
    assert normalize_departure_convenience(13.0, 9.0) == 50.0
    # Departure: 23:00 -> circular delta to 09:00 is min(14, 10) = 10 hours >= 8h max -> score 0.0
    assert normalize_departure_convenience(23.0, 9.0) == 0.0


def test_criteria_registry_coverage():
    # Verify core required criteria are registered
    assert "price" in CRITERIA_REGISTRY
    assert "duration" in CRITERIA_REGISTRY
    assert "departure_time" in CRITERIA_REGISTRY
    assert "flexibility" in CRITERIA_REGISTRY
    assert "customer_rating" in CRITERIA_REGISTRY
    assert "eco_score" in CRITERIA_REGISTRY


def test_ranking_and_explanation():
    offers = [
        Offer(
            offer_id="OFF-SR-0001",
            company="SolRuta",
            origin="Madrid",
            destination="Seville",
            travel_date="2026-07-12",
            departure_time="08:00",
            arrival_time="14:00",
            duration_minutes=360,
            price=20.0,
            transfers=1,
            luggage_kg=12,
            is_changeable=False,
            is_refundable=False,
            available_seats=20,
            customer_rating=3.9,
            co2_kg_per_passenger=18.0,
        ),
        Offer(
            offer_id="OFF-CE-0002",
            company="Camino Express",
            origin="Madrid",
            destination="Seville",
            travel_date="2026-07-12",
            departure_time="08:30",
            arrival_time="12:30",
            duration_minutes=240,
            price=55.0,
            transfers=0,
            luggage_kg=20,
            is_changeable=True,
            is_refundable=True,
            available_seats=15,
            customer_rating=4.8,
            co2_kg_per_passenger=12.0,
        ),
    ]

    # Speed-focused request
    req = TravellerRequest(
        destination="Seville",
        date_from="2026-07-12",
        date_to="2026-07-12",
        preferred_departure_window="08:30",
        weights={"duration": 0.50, "departure_time": 0.30, "price": 0.20}
    )

    ranker = RankingEngine()
    ranked = ranker.rank_offers(offers, req)

    assert len(ranked) == 2
    # Camino Express should win despite higher price due to duration and departure time
    assert ranked[0].offer.company == "Camino Express"
    assert ranked[0].rank == 1

    # Test explanation generation
    explanation = RecommendationExplainer.explain_top_offer(ranked, req)
    assert "Camino Express" in explanation
    assert "fastest journey" in explanation.lower() or "swift transit" in explanation.lower()
    assert "Trade-offs" in explanation
    assert "This offer is not objectively superior" in explanation
