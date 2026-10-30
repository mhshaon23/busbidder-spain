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
