"""
explainer.py
Generates a short explanation for the #1 ranked offer.
The project instructions say:
- Point out advantages (e.g. lowest price, direct route, flexible fare)
- Acknowledge disadvantages / trade-offs (e.g. costs more than cheapest, transfers)
- Don't claim it is 'objectively best', but explain it is best given the user's weights!
"""

from typing import List
from src.engine.ranker import RankedOffer
from src.models.request import TravellerRequest


class RecommendationExplainer:
    """
    Generates an explanation of why the top offer won the ranking.
    """
    @staticmethod
    def explain_top_offer(ranked_offers: List[RankedOffer], request: TravellerRequest) -> str:
        """
        Builds a human-readable text explanation comparing the #1 offer
        against the other offers in the search.
        """
        if not ranked_offers:
            return "No offers satisfied the mandatory constraints to formulate a recommendation."

        top = ranked_offers[0]
        offer = top.offer
        scores = top.criterion_scores

        strengths: List[str] = []
        trade_offs: List[str] = []

        # 1. Price comparison
        all_prices = [ro.offer.price for ro in ranked_offers]
        min_price = min(all_prices)
        if offer.price == min_price:
            strengths.append(f"lowest available price at EUR {offer.price:.2f}")
        elif scores.get("price", 0) > 75:
            strengths.append(f"competitive price (EUR {offer.price:.2f})")
        else:
            diff = offer.price - min_price
            trade_offs.append(f"costs EUR {diff:.2f} more than the cheapest option (EUR {min_price:.2f})")

        # 2. Duration & Transfers comparison
        all_durations = [ro.offer.duration_minutes for ro in ranked_offers]
        min_duration = min(all_durations)
        if offer.duration_minutes == min_duration:
            hours = int(offer.duration_minutes // 60)
            mins = int(offer.duration_minutes % 60)
            strengths.append(f"fastest journey time ({hours}h {mins:02d}m)")
        elif scores.get("duration", 0) > 75:
            hours = int(offer.duration_minutes // 60)
            mins = int(offer.duration_minutes % 60)
            strengths.append(f"quick trip ({hours}h {mins:02d}m)")
        else:
            extra_time = int(offer.duration_minutes - min_duration)
            trade_offs.append(f"takes {extra_time} minutes longer than the fastest option")

        if offer.transfers == 0:
            strengths.append("direct route with zero transfers")
        else:
            trade_offs.append(f"requires {offer.transfers} transfer(s)")

        # 3. Schedule comparison
        if scores.get("departure_time", 0) >= 85:
            strengths.append(f"convenient departure at {offer.departure_time_str} matching your {request.preferred_departure_window} window")
        elif scores.get("departure_time", 0) < 50:
            trade_offs.append(f"departure at {offer.departure_time_str} is further from your preferred departure time")

        # 4. Ticket flexibility
        if offer.is_changeable and offer.is_refundable:
            strengths.append("fully flexible ticket (both changeable and refundable)")
        elif not offer.is_changeable and not offer.is_refundable:
            trade_offs.append("strict non-flexible ticket (no changes or refunds)")
        elif offer.is_changeable and not offer.is_refundable:
            strengths.append("ticket can be changed")
            trade_offs.append("non-refundable")

        # 5. Environmental measure
        if offer.co2_kg_per_passenger < 10.0:
            strengths.append(f"low carbon footprint ({offer.co2_kg_per_passenger:.1f} kg CO2/passenger)")

        # Put everything together
        strengths_str = "; ".join(strengths) if strengths else "balanced attributes"
        trade_offs_str = "; ".join(trade_offs) if trade_offs else "no major disadvantages"

        top_weights = sorted(request.weights.items(), key=lambda x: x[1], reverse=True)
        main_priorities = ", ".join(f"{k} ({v*100:.0f}%)" for k, v in top_weights[:2])

        explanation = (
            f"Recommendation Explanation for Rank #1 ({offer.company} - {offer.offer_id}):\n"
            f"  * Total Score   : {top.weighted_total_score:.1f} / 100.0\n"
            f"  * Advantages    : {strengths_str.capitalize()}.\n"
            f"  * Trade-offs    : {trade_offs_str.capitalize()}.\n"
            f"  * Why it won    : Ranked #1 mainly because of your priority on {main_priorities}.\n"
            f"  * Note          : This offer is not objectively superior in every aspect; it is the best fit "
            f"under your specific constraints, scoring rules, and preference weights."
        )
        return explanation
