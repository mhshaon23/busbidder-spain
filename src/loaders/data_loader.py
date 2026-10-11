"""
Data loader module for BusBidder Spain.
Responsible for reading, type conversion, validation, logging, and quarantine of invalid records.
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
    Handles robust ingestion of system datasets with explicit validation
    and quarantine mechanism for non-compliant records.
    """
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (Path(__file__).resolve().parent.parent.parent / "data")
        self.companies: Dict[str, Company] = {}
        self.destinations: Dict[str, Destination] = {}
        self.known_destination_names: Set[str] = set()
        self.known_company_names: Set[str] = set()

    def load_all_metadata(self) -> None:
        """Loads companies and destinations to allow relational cross-validation."""
        self.load_companies()
        self.load_destinations()

    def load_companies(self, file_path: Optional[Path] = None) -> Dict[str, Company]:
        """Loads company profiles from JSON."""
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
        """Loads destination metadata from JSON."""
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
        Valid offers are parsed into Offer domain instances.
        Invalid/corrupt records are placed into quarantine and logged.
        """
        target_path = file_path or (self.data_dir / "offers.csv")
        quarantine_path = quarantine_file_path or (self.data_dir / "quarantine_offers.csv")

        # Ensure metadata is loaded for foreign-key-like integrity checks
        if not self.destinations:
            self.load_destinations()
        if not self.companies:
            self.load_companies()

        logger.info(f"Ingesting offer catalog from {target_path}")
        if not target_path.exists():
            raise FileNotFoundError(f"Offers file not found at {target_path}")

        valid_offers: List[Offer] = []
        quarantine_records: List[Dict[str, str]] = []

        with open(target_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=2):  # line 2 accounting for header
                offer_id = row.get("offer_id", f"ROW-{row_idx}").strip()
                try:
                    # 1. Foreign-key check: Destination
                    dest = row.get("destination", "").strip()
                    if dest not in self.known_destination_names:
                        raise DataValidationError(
                            f"Destination '{dest}' is not in registered destinations catalog.",
                            row_identifier=offer_id,
                            field="destination"
                        )

                    # 2. Foreign-key check: Company
                    company = row.get("company", "").strip()
                    if company not in self.known_company_names:
                        raise DataValidationError(
                            f"Company '{company}' is not in registered company list.",
                            row_identifier=offer_id,
                            field="company"
                        )

                    # 3. Domain entity creation with descriptor validation
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
                    # Quarantine invalid record
                    err_msg = str(err)
                    logger.warning(f"Quarantining record at line {row_idx} [{offer_id}]: {err_msg}")
                    quarantine_entry = dict(row)
                    quarantine_entry["line_number"] = str(row_idx)
                    quarantine_entry["rejection_reason"] = err_msg
                    quarantine_records.append(quarantine_entry)

        # Write quarantine records if any exist
        if quarantine_records:
            fieldnames = list(quarantine_records[0].keys())
            with open(quarantine_path, "w", newline="", encoding="utf-8") as qf:
                writer = csv.DictWriter(qf, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(quarantine_records)
            logger.info(f"Saved {len(quarantine_records)} rejected records to {quarantine_path}")

        logger.info(f"Data ingestion complete: {len(valid_offers)} accepted, {len(quarantine_records)} quarantined.")
        return valid_offers, quarantine_records
