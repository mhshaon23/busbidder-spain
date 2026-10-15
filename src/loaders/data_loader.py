"""
data_loader.py
Loads data files (JSON and CSV) for BusBidder Spain.
Task 2 requirements implemented:
- Read companies.json and destinations.json
- Read offers.csv and convert fields into domain objects
- Check foreign keys (destination must exist, company must exist)
- If a row is invalid, quarantine it in data/quarantine_offers.csv with the reason
- Log loading events and errors into busbidder.log
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from src.models.company import Company
from src.models.destination import Destination
from src.models.offer import Offer
from src.validators.exceptions import (
    DataValidationError,
    CorruptRecordError,
    InvalidIdentifierError,
)
from src.loaders.logger import logger


class DataLoader:
    """
    Handles reading the files from the data folder and validating them.
    Invalid rows are sent to a quarantine file so the app doesn't crash.
    """
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (Path(__file__).resolve().parent.parent.parent / "data")
        self.companies: Dict[str, Company] = {}
        self.destinations: Dict[str, Destination] = {}
        self.known_destination_names: Set[str] = set()
        self.known_company_names: Set[str] = set()

    def load_all_metadata(self) -> None:
        """Helper to load both companies and destinations at once."""
        self.load_companies()
        self.load_destinations()

    def load_companies(self, file_path: Optional[Path] = None) -> Dict[str, Company]:
        """Loads the 5 bus companies from data/companies.json."""
        target_path = file_path or (self.data_dir / "companies.json")
        logger.info(f"Loading companies from {target_path}")

        if not target_path.exists():
            raise FileNotFoundError(f"Companies file not found at {target_path}")

        with open(target_path, "r", encoding="utf-8") as f:
            raw_companies = json.load(f)

        self.companies.clear()
        self.known_company_names.clear()

        for item in raw_companies:
            comp = Company(
                name=item["name"],
                code=item["code"],
                profile=item["profile"],
                default_cancellation_policy=item["default_cancellation_policy"],
                eco_certified=item.get("eco_certified", False),
            )
            self.companies[comp.name] = comp
            self.known_company_names.add(comp.name)

        logger.info(f"Loaded {len(self.companies)} companies successfully.")
        return self.companies

    def load_destinations(self, file_path: Optional[Path] = None) -> Dict[str, Destination]:
        """Loads the 15 destinations from data/destinations.json."""
        target_path = file_path or (self.data_dir / "destinations.json")
        logger.info(f"Loading destinations from {target_path}")

        if not target_path.exists():
            raise FileNotFoundError(f"Destinations file not found at {target_path}")

        with open(target_path, "r", encoding="utf-8") as f:
            raw_dests = json.load(f)

        self.destinations.clear()
        self.known_destination_names.clear()

        for item in raw_dests:
            dest = Destination(
                name=item["name"],
                distance_km=item["distance_km"],
                region=item["region"],
                is_coastal=item["is_coastal"],
            )
            self.destinations[dest.name] = dest
            self.known_destination_names.add(dest.name)

        logger.info(f"Loaded {len(self.destinations)} destinations successfully.")
        return self.destinations

    def load_offers(
        self,
        file_path: Optional[Path] = None,
        quarantine_file_path: Optional[Path] = None,
    ) -> Tuple[List[Offer], List[Dict[str, str]]]:
        """
        Loads and validates offers from CSV.
        Valid offers are parsed into Offer objects.
        Corrupt or invalid rows are quarantined into a separate CSV and logged.
        """
        target_path = file_path or (self.data_dir / "offers.csv")
        quarantine_path = quarantine_file_path or (self.data_dir / "quarantine_offers.csv")

        # Make sure company and destination data is already loaded so we can check foreign keys
        if not self.destinations:
            self.load_destinations()
        if not self.companies:
            self.load_companies()

        logger.info(f"Loading offers from {target_path}")
        if not target_path.exists():
            raise FileNotFoundError(f"Offers file not found at {target_path}")

        valid_offers: List[Offer] = []
        quarantine_records: List[Dict[str, str]] = []

        with open(target_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                offer_id = row.get("offer_id", f"ROW-{row_idx}").strip()
                try:
                    # 1. Check destination is valid
                    dest = row.get("destination", "").strip()
                    if dest not in self.known_destination_names:
                        raise DataValidationError(
                            f"Destination '{dest}' is not in registered destinations catalog.",
                            row_identifier=offer_id,
                            field="destination"
                        )

                    # 2. Check company is valid
                    company = row.get("company", "").strip()
                    if company not in self.known_company_names:
                        raise DataValidationError(
                            f"Company '{company}' is not in registered company list.",
                            row_identifier=offer_id,
                            field="company"
                        )

                    # 3. Create Offer instance (descriptors will validate numeric fields and regex)
                    offer = Offer(
                        offer_id=offer_id,
                        company=company,
                        origin=row.get("origin", "Madrid"),
                        destination=dest,
                        travel_date=row.get("travel_date", ""),
                        departure_time=row.get("departure_time", ""),
                        arrival_time=row.get("arrival_time", ""),
                        duration_minutes=int(row.get("duration_minutes", 0)),
                        price=float(row.get("price", 0.0)),
                        transfers=int(row.get("transfers", 0)),
                        luggage_kg=int(row.get("luggage_kg", 0)),
                        is_changeable=row.get("is_changeable", "").strip().lower() in ("true", "1", "yes"),
                        is_refundable=row.get("is_refundable", "").strip().lower() in ("true", "1", "yes"),
                        available_seats=int(row.get("available_seats", 0)),
                        customer_rating=float(row.get("customer_rating", 0.0)),
                        co2_kg_per_passenger=float(row.get("co2_kg_per_passenger", 12.0)),
                    )
                    valid_offers.append(offer)

                except Exception as err:
                    # If any validation error happens, quarantine the row
                    err_msg = str(err)
                    logger.warning(f"Quarantining record at line {row_idx} [{offer_id}]: {err_msg}")
                    quarantine_entry = dict(row)
                    quarantine_entry["line_number"] = str(row_idx)
                    quarantine_entry["rejection_reason"] = err_msg
                    quarantine_records.append(quarantine_entry)

        # Write quarantined rows to file if there are any
        if quarantine_records:
            fieldnames = list(quarantine_records[0].keys())
            with open(quarantine_path, "w", newline="", encoding="utf-8") as qf:
                writer = csv.DictWriter(qf, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(quarantine_records)
            logger.info(f"Saved {len(quarantine_records)} quarantined records to {quarantine_path}")

        logger.info(f"Finished loading: {len(valid_offers)} valid offers, {len(quarantine_records)} quarantined.")
        return valid_offers, quarantine_records
