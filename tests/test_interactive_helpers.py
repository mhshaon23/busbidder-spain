"""
Tests for the traveller's own hard constraints in interactive mode,
the hard/soft summary shown to the user, and the missing-file error.
"""

import pytest
from main import apply_user_constraints
from src.cli.interface import describe_request
from src.loaders.data_loader import DataLoader
from src.profiles.archetypes import (
    create_business_traveller_request,
    create_balanced_traveller_request,
)
from src.validators.exceptions import DataFileMissingError, BusBidderError


def _limits(**overrides):
    limits = {
        "max_budget": None,
        "max_transfers": None,
        "max_duration_minutes": None,
        "min_luggage_kg": 0,
        "require_changeable": False,
        "require_refundable": False,
        "preferred_departure": None,
    }
    limits.update(overrides)
    return limits


def test_specification_example_request_is_applied():
    # Spec example: Madrid-Malaga, 12-14 July, max EUR 50, morning, max 1 transfer, changeable required
    req = create_balanced_traveller_request("Malaga", "2026-07-12", "2026-07-14")
    apply_user_constraints(req, _limits(max_budget=50.0, max_transfers=1,
                                        require_changeable=True, preferred_departure="Morning"))

    assert req.max_budget == 50.0
    assert req.max_transfers == 1
    assert req.require_changeable is True
    assert req.preferred_departure_window == "Morning"


def test_stricter_limit_wins_when_combined_with_profile():
    # Business profile already demands 0 transfers; a traveller saying "max 2" must not loosen it
    req = create_business_traveller_request()
    apply_user_constraints(req, _limits(max_transfers=2, max_budget=60.0))

    assert req.max_transfers == 0
    assert req.max_budget == 60.0
    assert req.require_changeable is True


def test_summary_separates_hard_and_soft_conditions():
    req = create_balanced_traveller_request()
    apply_user_constraints(req, _limits(max_budget=50.0, require_changeable=True))
    text = describe_request(req)

    hard, soft = text.split("SOFT PREFERENCES")
    assert "EUR 50.00" in hard and "Changeable ticket    : required" in hard
    assert "Preferred departure" in soft and "Weight price" in soft


def test_missing_data_file_raises_custom_error(tmp_path):
    loader = DataLoader(data_dir=tmp_path)
    with pytest.raises(DataFileMissingError):
        loader.load_companies()
    # The custom error is part of the application's error hierarchy
    assert issubclass(DataFileMissingError, BusBidderError)


def test_profile_limits_become_suggestions_so_first_search_shows_all():
    # Budget profile has max EUR 45 and max 1 transfer built in
    from main import split_profile_limits
    from src.profiles.archetypes import create_budget_traveller_request
    req = create_budget_traveller_request("Malaga", "2026-07-12", "2026-07-14")
    suggestions = split_profile_limits(req)

    assert suggestions == {"max_budget": 45.0, "max_transfers": 1}
    assert req.max_budget is None and req.max_transfers is None


def test_specification_example_through_refine_step():
    # Balanced profile, all offers first, then refine with EUR 50, 1 transfer, changeable
    from main import split_profile_limits
    from src.engine.filters import FilterEngine
    from src.engine.ranker import RankingEngine
    offers, _ = DataLoader().load_offers()
    req = create_balanced_traveller_request("Malaga", "2026-07-12", "2026-07-14")
    split_profile_limits(req)
    first = FilterEngine().filter_offers(offers, req).accepted_offers
    assert len(first) == 15

    apply_user_constraints(req, _limits(max_budget=50.0, max_transfers=1, require_changeable=True))
    refined = FilterEngine().filter_offers(first, req).accepted_offers
    ranked = RankingEngine().rank_offers(refined, req)
    assert len(refined) == 9
    assert ranked[0].offer.offer_id == "OFF-CL-1052"


def test_note_when_all_remaining_tickets_are_fully_flexible():
    from main import uniform_criteria_notes
    from src.engine.filters import FilterEngine
    offers, _ = DataLoader().load_offers()
    req = create_balanced_traveller_request("Malaga", "2026-07-12", "2026-07-14")
    apply_user_constraints(req, _limits(require_changeable=True, require_refundable=True))
    remaining = FilterEngine().filter_offers(offers, req).accepted_offers

    notes = uniform_criteria_notes(remaining, req)
    assert any("fully flexible" in n for n in notes)
    # Price still differs, so no note about price
    assert not any("price" in n for n in notes)
