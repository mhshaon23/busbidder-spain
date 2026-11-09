"""
ranker.py
RankingEngine that scores and sorts surviving offers based on user weights.
Formula: Total Score = sum(weight_i * normalized_score_i)
"""

from typing import List, Dict, Any
from src.models.offer import Offer
from src.models.request import TravellerRequest
from src.validators.exceptions import RankingConfigurationError, WeightValidationError
from src.engine.criteria import CRITERIA_REGISTRY
from src.loaders.logger import logger


class RankedOffer:
    """
    Holds an Offer alongside its individual criterion scores (0-100)
    and final weighted total score.
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
        """Convert to dict for easy printing and debugging."""
        data = self.offer.to_dict()
        data["rank"] = self.rank
        data["total_score"] = round(self.weighted_total_score, 2)
        for crit, score in self.criterion_scores.items():
            data[f"score_{crit}"] = round(score, 1)
        return data

    def __repr__(self) -> str:
        return (
            f"<RankedOffer #{self.rank} | {self.offer.company} | "
            f"Score: {self.weighted_total_score:.2f} | Price: EUR {self.offer.price:.2f}>"
        )


class RankingEngine:
    """
    Ranks filtered offers according to the traveller's preference weights.
    """
    def rank_offers(self, offers: List[Offer], request: TravellerRequest) -> List[RankedOffer]:
        """
        Calculates normalized scores for each requested criterion,
        multiplies them by user weights, and sorts descending by total score.
        """
        if not offers:
            logger.info("No offers to rank.")
            return []

        # Make sure all weights the user requested exist in our registry
        for crit_name in request.weights.keys():
            if crit_name not in CRITERIA_REGISTRY:
                raise RankingConfigurationError(
                    f"Criterion '{crit_name}' is not in the registry. "
                    f"Available criteria: {list(CRITERIA_REGISTRY.keys())}"
                )

        ranked_list: List[RankedOffer] = []

        # Calculate scores for each offer
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
        # 1. Total score (highest first)
        # 2. Tie breaker: lower price
        # 3. Tie breaker: higher customer rating
        # 4. Tie breaker: shorter duration
        ranked_list.sort(
            key=lambda ro: (
                round(ro.weighted_total_score, 4),
                -ro.offer.price,
                ro.offer.customer_rating,
                -ro.offer.duration_minutes
            ),
            reverse=True
        )

        # Assign rank number (1, 2, 3...)
        for idx, item in enumerate(ranked_list, start=1):
            item.rank = idx

        logger.info(f"Ranked {len(ranked_list)} offers. Top offer is {ranked_list[0].offer.offer_id}")
        return ranked_list
