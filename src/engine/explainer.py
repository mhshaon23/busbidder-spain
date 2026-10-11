"""
Explainability generator for BusBidder Spain recommendations.
Produces natural language explanations articulating strengths, trade-offs,
and decision weights without claiming objective supremacy.
"""

from typing import List, Dict, Any
from src.engine.ranker import RankedOffer
from src.models.request import TravellerRequest


class RecommendationExplainer:
    """
    Generates explainable, data-driven rationales for top-ranked offers,
    directly fulfilling Section 6 requirements.
    """
    @staticmethod
    def explain_top_offer(ranked_offers: List[RankedOffer], request: TravellerRequest) -> str:
        """
        Produces a nuanced textual explanation of why the top offer ranked highest,
        highlighting both advantages and remaining disadvantages.
        """
        if not ranked_offers:
            return "No offers satisfied the mandatory constraints to formulate a recommendation."

        top = ranked_offers[0]
        offer = top.offer
        scores = top.criterion_scores

        strengths: List[str] = []
        trade_offs: List[str] = []

        # 1. Price analysis
        all_prices = [ro.offer.price for ro in ranked_offers]
        min_price = min(all_prices)
        if offer.price == min_price:
            strengths.append(f"lowest available price at €{offer.price:.2f}")
        elif scores.get("price", 0) > 75:
            strengths.append(f"highly competitive fare (€{offer.price:.2f})")
        else:
            diff = offer.price - min_price
            trade_offs.append(f"costs €{diff:.2f} more than the cheapest alternative (€{min_price:.2f})")

        # 2. Duration & Transfers analysis
        all_durations = [ro.offer.duration_minutes for ro in ranked_offers]
        min_duration = min(all_durations)
        if offer.duration_minutes == min_duration:
            strengths.append(f"fastest journey time ({offer.duration_minutes // 60}h {offer.duration_minutes % 60}m)")
        elif scores.get("duration", 0) > 75:
            strengths.append(f"swift transit ({offer.duration_minutes // 60}h {offer.duration_minutes % 60}m)")
        else:
            extra_time = offer.duration_minutes - min_duration
            trade_offs.append(f"takes {extra_time} minutes longer than the fastest option")

        if offer.transfers == 0:
            strengths.append("direct route with zero transfers")
        else:
            trade_offs.append(f"requires {offer.transfers} transfer(s)")

        # 3. Schedule convenience
        if scores.get("departure_time", 0) >= 85:
            strengths.append(f"convenient departure at {offer.departure_time_str} aligning with your {request.preferred_departure_window} window")
        elif scores.get("departure_time", 0) < 50:
            trade_offs.append(f"departure at {offer.departure_time_str} is somewhat distant from preferred target time")

        # 4. Flexibility & conditions
        if offer.is_changeable and offer.is_refundable:
            strengths.append("maximum flexibility (both changeable and refundable)")
        elif not offer.is_changeable and not offer.is_refundable:
            trade_offs.append("strict non-flexible fare (no cancellations or rebooking)")
        elif offer.is_changeable and not offer.is_refundable:
            strengths.append("changeable fare")
            trade_offs.append("non-refundable")

        # 5. Eco rating
        if offer.co2_kg_per_passenger < 10.0:
            strengths.append(f"low environmental impact ({offer.co2_kg_per_passenger:.1f} kg CO2/passenger)")

        # Synthesize into clear, structured explanation
        strengths_str = "; ".join(strengths) if strengths else "balanced overall attributes"
        trade_offs_str = "; ".join(trade_offs) if trade_offs else "no significant drawbacks identified"

        highest_weighted = sorted(request.weights.items(), key=lambda x: x[1], reverse=True)
        primary_criteria_str = ", ".join(f"{k} ({v*100:.0f}%)" for k, v in highest_weighted[:2])

        explanation = (
            f"Recommendation Rationale for #{top.rank} ({offer.company} - {offer.offer_id}):\n"
            f"  * Composite Score : {top.weighted_total_score:.1f}/100.0\n"
            f"  * Key Advantages  : {strengths_str.capitalize()}.\n"
            f"  * Trade-offs      : {trade_offs_str.capitalize()}.\n"
            f"  * Weight Alignment: Ranked highest primarily due to your high emphasis on {primary_criteria_str}.\n"
            f"  * Notice          : This offer is not objectively superior in every aspect; it represents "
            f"the optimal compromise strictly under your configured constraints, weights, and scoring rules."
        )
        return explanation
