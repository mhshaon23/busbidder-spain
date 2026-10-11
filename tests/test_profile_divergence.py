"""
Sensitivity analysis tests: verifying that different traveller profiles
produce distinct top recommendations on the identical dataset pool.
"""

import pytest
from src.loaders.data_loader import DataLoader
from src.engine.filters import FilterEngine
from src.engine.ranker import RankingEngine
from src.profiles.archetypes import (
    create_budget_traveller_request,
    create_business_traveller_request,
    create_eco_traveller_request,
)


@pytest.fixture
def catalog_offers():
    loader = DataLoader()
    offers, _ = loader.load_offers()
    return offers


def test_profile_divergence_on_identical_destination(catalog_offers):
    filter_engine = FilterEngine()
    ranker = RankingEngine()

    destination = "Malaga"
    date_from = "2026-07-12"
    date_to = "2026-07-14"

    # Profile 1: Budget Backpacker
    budget_req = create_budget_traveller_request(destination, date_from, date_to, max_budget=45.0)
    budget_surviving = filter_engine.filter_offers(catalog_offers, budget_req).accepted_offers
    budget_ranked = ranker.rank_offers(budget_surviving, budget_req)

    # Profile 2: Business Executive
    business_req = create_business_traveller_request(destination, date_from, date_to)
    business_surviving = filter_engine.filter_offers(catalog_offers, business_req).accepted_offers
    business_ranked = ranker.rank_offers(business_surviving, business_req)

    # Profile 3: Eco-Conscious Traveller
    eco_req = create_eco_traveller_request(destination, date_from, date_to)
    eco_surviving = filter_engine.filter_offers(catalog_offers, eco_req).accepted_offers
    eco_ranked = ranker.rank_offers(eco_surviving, eco_req)

    # All three profiles must find surviving offers
    assert len(budget_ranked) > 0
    assert len(business_ranked) > 0
    assert len(eco_ranked) > 0

    top_budget = budget_ranked[0].offer
    top_business = business_ranked[0].offer
    top_eco = eco_ranked[0].offer

    # Verify that different priorities led to distinct winning companies or offers
    # Budget should pick the low-cost or coastal carrier
    assert top_budget.company in ("SolRuta", "CostaLink")
    assert top_budget.price <= 35.0

    # Business must be direct with flexible conditions
    assert top_business.transfers == 0
    assert top_business.is_changeable is True
    assert top_business.company == "Camino Express"

    # Eco should pick VerdeBus due to lowest CO2
    assert top_eco.company == "VerdeBus"

    # Crucially, top business is different from top budget
    assert top_business.offer_id != top_budget.offer_id
