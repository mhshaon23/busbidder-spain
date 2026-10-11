"""
Weighted multi-criteria ranking engine for BusBidder Spain.
Combines normalized scores with user-defined preference weights.
"""

from typing import List, Dict, Any
from src.models.offer import Offer
from src.models.request import TravellerRequest
from src.validators.exceptions import RankingConfigurationError, WeightValidationError
from src.engine.criteria import CRITERIA_REGISTRY
from src.loaders.logger import logger


class RankedOffer:
    """
    Encapsulates an offer along with its component scores and final weighted composite score.
    Supports complete auditing and explainability.
    """
    def __init__(
        self,
        offer: Offer,
        criterion_scores: Dict[str, float],
        weighted_total_score: float,
        rank: int = 0
    ):
        self.offer = offer
        self.criterion_scores = criterion_scores
        self.weighted_total_score = weighted_total_score
        self.rank = rank

    def to_dict(self) -> Dict[str, Any]:
        """Dictionary format for reporting or tabular views."""
        data = self.offer.to_dict()
        data["rank"] = self.rank
        data["total_score"] = round(self.weighted_total_score, 2)
        for crit, score in self.criterion_scores.items():
            data[f"score_{crit}"] = round(score, 1)
        return data

    def __repr__(self) -> str:
        return (
            f"<RankedOffer #{self.rank} | {self.offer.company} | "
            f"Score: {self.weighted_total_score:.2f} | Price: €{self.offer.price:.2f}>"
        )


class RankingEngine:
    """
    Calculates multi-criteria weighted scores and produces a deterministic ranking.
    """
    def rank_offers(self, offers: List[Offer], request: TravellerRequest) -> List[RankedOffer]:
        """
        Ranks surviving offers according to request weights.
        """
        if not offers:
            logger.info("Ranking requested on empty offer collection.")
            return []

        # Validate that all requested weights exist in registry
        for crit_name in request.weights.keys():
            if crit_name not in CRITERIA_REGISTRY:
                raise RankingConfigurationError(
                    f"Requested criterion '{crit_name}' is not registered. "
                    f"Available criteria: {list(CRITERIA_REGISTRY.keys())}"
                )

        ranked_list: List[RankedOffer] = []

        for offer in offers:
            criterion_scores: Dict[str, float] = {}
            weighted_total = 0.0

            for crit_name, weight in request.weights.items():
                eval_func = CRITERIA_REGISTRY[crit_name]
                score = eval_func(offers, offer, request)
                criterion_scores[crit_name] = score
                weighted_total += weight * score

            ranked_list.append(
                RankedOffer(
                    offer=offer,
                    criterion_scores=criterion_scores,
                    weighted_total_score=weighted_total,
                )
            )

        # Deterministic sorting:
        # Primary: weighted total score (descending)
        # Secondary tie-breakers: lower price, higher rating, shorter duration
        ranked_list.sort(
            key=lambda ro: (
                round(ro.weighted_total_score, 4),
                -ro.offer.price,
                ro.offer.customer_rating,
                -ro.offer.duration_minutes
            ),
            reverse=True
        )

        # Assign final rank position
        for idx, item in enumerate(ranked_list, start=1):
            item.rank = idx

        logger.info(f"Successfully ranked {len(ranked_list)} offers. Top offer: {ranked_list[0].offer.offer_id}")
        return ranked_list
