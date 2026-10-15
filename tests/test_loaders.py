"""
Unit tests for data loader, file ingestion, and quarantine mechanism.
"""

from pathlib import Path
import pytest
from src.loaders.data_loader import DataLoader
from src.validators.exceptions import DataValidationError


def test_load_metadata():
    loader = DataLoader()
    companies = loader.load_companies()
    destinations = loader.load_destinations()

    assert len(companies) == 5
    assert "SolRuta" in companies
    assert "VerdeBus" in companies

    assert len(destinations) == 15
    assert "Barcelona" in destinations
    assert "Toledo" in destinations


def test_load_valid_offers():
    loader = DataLoader()
    offers, quarantined = loader.load_offers()

    assert len(offers) >= 75
    assert len(quarantined) == 0
    # Every offer should have origin Madrid
    assert all(o.origin == "Madrid" for o in offers)


def test_quarantine_corrupt_offers(tmp_path):
    loader = DataLoader()
    corrupt_csv = Path(__file__).resolve().parent.parent / "data" / "corrupt_offers_sample.csv"
    quarantine_output = tmp_path / "test_quarantine.csv"

    valid, quarantined = loader.load_offers(
        file_path=corrupt_csv,
        quarantine_file_path=quarantine_output
    )

    # In our corrupt sample, all 5 rows were intentionally flawed
    assert len(valid) == 0
    assert len(quarantined) == 5
    assert quarantine_output.exists()

    # Verify that rejection reasons were captured
    reasons = [row["rejection_reason"] for row in quarantined]
    assert any("strictly > 0" in r for r in reasons)  # Negative price
    assert any("not in registered destinations" in r for r in reasons)  # Unknown destination
    assert any("Offer ID" in r for r in reasons)  # Bad ID regex
    assert any("between 1.0 and 5.0" in r for r in reasons)  # Rating > 5.0
    assert any("Temporal inconsistency" in r for r in reasons)  # Inconsistent duration


def test_missing_file_raises():
    loader = DataLoader()
    non_existent = Path("non_existent_offers.csv")
    with pytest.raises(FileNotFoundError):
        loader.load_offers(file_path=non_existent)

