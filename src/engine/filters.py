"""
Hard constraint filtering engine for BusBidder Spain.
Separates mandatory restrictions from soft ranking preferences.
"""

from typing import List, Tuple, Dict
from src.models.offer import Offer
from src.models.request import TravellerRequest
from src.loaders.logger import logger


class FilterResult:
    """Encapsulates the output of the filtering stage with audit statistics."""
    def __init__(self, accepted_offers: List[Offer], rejection_counts: Dict[str, int]):
        self.accepted_offers = accepted_offers
        self.rejection_counts = rejection_counts
        self.total_initial = len(accepted_offers) + sum(rejection_counts.values())

    @property
    def survival_rate(self) -> float:
        """Percentage of offers that passed hard constraints."""
        if self.total_initial == 0:
            return 0.0
        return (len(self.accepted_offers) / self.total_initial) * 100.0


class FilterEngine:
    """
    Applies non-negotiable hard constraints to remove unacceptable offers
    prior to multi-criteria ranking.
    """
    def filter_offers(self, offers: List[Offer], request: TravellerRequest) -> FilterResult:
        """
        Evaluates a collection of offers against traveller constraints.
        Returns accepted offers alongside a statistical breakdown of rejection causes.
        """
        accepted: List[Offer] = []
        rejections: Dict[str, int] = {
            "destination_mismatch": 0,
            "date_out_of_window": 0,
            "insufficient_seats": 0,
            "exceeded_budget": 0,
            "exceeded_transfers": 0,
            "exceeded_duration": 0,
            "insufficient_luggage": 0,
            "missing_changeability": 0,
            "missing_refundability": 0,
        }

        for offer in offers:
            # 1. Destination check
            if offer.destination.lower() != request.destination.lower():
                rejections["destination_mismatch"] += 1
                continue

            # 2. Travel date window
            if not (request.date_from <= offer.travel_date <= request.date_to):
                rejections["date_out_of_window"] += 1
                continue

            # 3. Available seats
            if offer.available_seats < request.min_seats:
                rejections["insufficient_seats"] += 1
                continue

            # 4. Maximum budget
            if request.max_budget is not None and offer.price > request.max_budget:
                rejections["exceeded_budget"] += 1
                continue

            # 5. Maximum transfers
            if request.max_transfers is not None and offer.transfers > request.max_transfers:
                rejections["exceeded_transfers"] += 1
                continue

            # 6. Maximum journey duration
            if request.max_duration_minutes is not None and offer.duration_minutes > request.max_duration_minutes:
                rejections["exceeded_duration"] += 1
                continue

            # 7. Minimum luggage requirement
            if offer.luggage_kg < request.min_luggage_kg:
                rejections["insufficient_luggage"] += 1
                continue

            # 8. Mandatory ticket flexibility constraints
            if request.require_changeable and not offer.is_changeable:
                rejections["missing_changeability"] += 1
                continue

            if request.require_refundable and not offer.is_refundable:
                rejections["missing_refundability"] += 1
                continue

            # All mandatory constraints satisfied
            accepted.append(offer)

        logger.info(
            f"Filtering complete for {request.destination}: "
            f"{len(accepted)} accepted from {len(offers)} initial offers."
        )
        return FilterResult(accepted_offers=accepted, rejection_counts=rejections)

