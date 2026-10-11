"""
Unit tests for the hard constraint filtering engine.
"""

import pytest
from src.loaders.data_loader import DataLoader
from src.engine.filters import FilterEngine
from src.models.request import TravellerRequest


@pytest.fixture
def all_offers():
    loader = DataLoader()
    offers, _ = loader.load_offers()
    return offers


def test_filter_destination_and_dates(all_offers):
    filter_engine = FilterEngine()
    req = TravellerRequest(
        destination="Valencia",
        date_from="2026-07-12",
        date_to="2026-07-12",
    )
    result = filter_engine.filter_offers(all_offers, req)
    
    assert len(result.accepted_offers) > 0
    assert all(o.destination == "Valencia" for o in result.accepted_offers)
    assert all(o.travel_date_str == "2026-07-12" for o in result.accepted_offers)
    assert result.rejection_counts["destination_mismatch"] > 0


def test_filter_budget_constraint(all_offers):
    filter_engine = FilterEngine()
    # Extremely tight budget
    req = TravellerRequest(
        destination="Barcelona",
        date_from="2026-07-12",
        date_to="2026-07-14",
        max_budget=20.0,
    )
    result = filter_engine.filter_offers(all_offers, req)
    
    # All accepted offers must be <= 20.0
    for o in result.accepted_offers:
        assert o.price <= 20.0
    assert result.rejection_counts["exceeded_budget"] > 0


def test_filter_direct_only_transfers(all_offers):
    filter_engine = FilterEngine()
    req = TravellerRequest(
        destination="Cadiz",
        date_from="2026-07-12",
        date_to="2026-07-14",
        max_transfers=0,
    )
    result = filter_engine.filter_offers(all_offers, req)
    for o in result.accepted_offers:
        assert o.transfers == 0


def test_filter_mandatory_flexibility(all_offers):
    filter_engine = FilterEngine()
    req = TravellerRequest(
        destination="Malaga",
        date_from="2026-07-12",
        date_to="2026-07-14",
        require_refundable=True,
    )
    result = filter_engine.filter_offers(all_offers, req)
    for o in result.accepted_offers:
        assert o.is_refundable is True
    assert result.rejection_counts["missing_refundability"] > 0
