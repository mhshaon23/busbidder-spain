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



def test_missing_field_values_are_quarantined(tmp_path):
    """Missing data: rows with an empty price or missing departure time are set aside, not guessed."""
    header = (
        "offer_id,company,origin,destination,travel_date,departure_time,arrival_time,duration_minutes,"
        "price,transfers,luggage_kg,is_changeable,is_refundable,available_seats,customer_rating,co2_kg_per_passenger\n"
    )
    rows = (
        "OFF-SR-8001,SolRuta,Madrid,Toledo,2026-07-12,08:00,09:00,60,,0,12,False,False,10,3.9,3.0\n"
        "OFF-SR-8002,SolRuta,Madrid,Toledo,2026-07-12,,09:00,60,12.5,0,12,False,False,10,3.9,3.0\n"
        "OFF-SR-8003,SolRuta,Madrid,Toledo,2026-07-12,08:00,09:00,60,12.5,0,12,False,False,10,3.9,3.0\n"
    )
    csv_path = tmp_path / "missing_values.csv"
    csv_path.write_text(header + rows, encoding="utf-8")

    valid, quarantined = DataLoader().load_offers(
        file_path=csv_path, quarantine_file_path=tmp_path / "q.csv"
    )

    assert [o.offer_id for o in valid] == ["OFF-SR-8003"]
    assert {q["offer_id"] for q in quarantined} == {"OFF-SR-8001", "OFF-SR-8002"}


def test_offer_with_zero_seats_loads_but_is_filtered():
    """Boundary: 0 seats is valid catalogue data (sold out), but the filter must remove it."""
    from src.engine.filters import FilterEngine
    from src.models.request import TravellerRequest

    offers, _ = DataLoader().load_offers()
    target = next(o for o in offers if o.destination == "Toledo")
    target.available_seats = 0
    request = TravellerRequest(destination="Toledo", date_from="2026-07-12", date_to="2026-07-14")

    result = FilterEngine().filter_offers(offers, request)

    assert target not in result.accepted_offers
    assert result.rejection_counts["insufficient_seats"] == 1
