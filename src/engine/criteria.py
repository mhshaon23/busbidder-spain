"""
Pluggable criteria registry for BusBidder Spain ranking engine.
Implements the registry pattern via function decorators (Task 7 requirement).
"""

from typing import Callable, Dict, List, Any
from src.models.offer import Offer
from src.models.request import TravellerRequest
from src.engine.normalizers import (
    normalize_cost_criterion,
    normalize_benefit_criterion,
    normalize_departure_convenience,
)

# Global criterion registry
CRITERIA_REGISTRY: Dict[str, Callable[[List[Offer], Offer, TravellerRequest], float]] = {}


def register_criterion(name: str):
    """
    Decorator that registers a criterion evaluation function into the central registry.
    Demonstrates extensible metaprogramming.
    """
    def decorator(func: Callable[[List[Offer], Offer, TravellerRequest], float]):
        CRITERIA_REGISTRY[name] = func
        return func
    return decorator


@register_criterion("price")
def evaluate_price(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates ticket price (lower is better)."""
    all_prices = [o.price for o in offers]
    return normalize_cost_criterion(all_prices, target_offer.price)


@register_criterion("duration")
def evaluate_duration(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates journey duration in minutes (lower is better)."""
    all_durations = [float(o.duration_minutes) for o in offers]
    return normalize_cost_criterion(all_durations, float(target_offer.duration_minutes))


@register_criterion("departure_time")
def evaluate_departure_time(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates departure time convenience relative to target traveller hour."""
    dep_hour = target_offer.departure_time.hour + target_offer.departure_time.minute / 60.0
    return normalize_departure_convenience(dep_hour, request.target_hour)


@register_criterion("flexibility")
def evaluate_flexibility(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates fare flexibility (higher is better, combining changeable & refundable)."""
    all_flex = [o.flexibility_score for o in offers]
    return normalize_benefit_criterion(all_flex, target_offer.flexibility_score)


@register_criterion("customer_rating")
def evaluate_rating(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates customer rating (higher is better)."""
    all_ratings = [o.customer_rating for o in offers]
    return normalize_benefit_criterion(all_ratings, target_offer.customer_rating)


@register_criterion("eco_score")
def evaluate_eco_score(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates CO2 emissions (lower CO2 per passenger is better)."""
    all_co2 = [o.co2_kg_per_passenger for o in offers]
    return normalize_cost_criterion(all_co2, target_offer.co2_kg_per_passenger)
