"""
criteria.py
Evaluation criteria functions for ranking offers.
I used a decorator @register_criterion to build a criteria registry.
This makes it easy to add new criteria without changing the main ranking code.
"""

from typing import Callable, Dict, List
from src.models.offer import Offer
from src.models.request import TravellerRequest
from src.engine.normalizers import (
    normalize_cost_criterion,
    normalize_benefit_criterion,
    normalize_departure_convenience,
)

# Registry dictionary mapping criterion names to their evaluation functions
CRITERIA_REGISTRY: Dict[str, Callable[[List[Offer], Offer, TravellerRequest], float]] = {}


def register_criterion(name: str):
    """
    Decorator that registers a criterion function in CRITERIA_REGISTRY.
    Demonstrates metaprogramming / decorators as required in the project specification.
    """
    def decorator(func: Callable[[List[Offer], Offer, TravellerRequest], float]):
        CRITERIA_REGISTRY[name] = func
        return func
    return decorator


@register_criterion("price")
def evaluate_price(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates ticket price: lower price is better."""
    all_prices = [o.price for o in offers]
    return normalize_cost_criterion(all_prices, target_offer.price)


@register_criterion("duration")
def evaluate_duration(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates journey duration: shorter duration is better."""
    all_durations = [float(o.duration_minutes) for o in offers]
    return normalize_cost_criterion(all_durations, float(target_offer.duration_minutes))


@register_criterion("departure_time")
def evaluate_departure_time(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates how close departure time is to the user's preferred time."""
    dep_hour = target_offer.departure_time.hour + target_offer.departure_time.minute / 60.0
    return normalize_departure_convenience(dep_hour, request.target_hour)


@register_criterion("flexibility")
def evaluate_flexibility(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates ticket flexibility (changeable / refundable): higher is better."""
    all_flex = [o.flexibility_score for o in offers]
    return normalize_benefit_criterion(all_flex, target_offer.flexibility_score)


@register_criterion("customer_rating")
def evaluate_rating(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates customer star rating: higher rating is better."""
    all_ratings = [o.customer_rating for o in offers]
    return normalize_benefit_criterion(all_ratings, target_offer.customer_rating)


@register_criterion("eco_score")
def evaluate_eco_score(offers: List[Offer], target_offer: Offer, request: TravellerRequest) -> float:
    """Evaluates CO2 emissions per passenger: lower emissions is better."""
    all_co2 = [o.co2_kg_per_passenger for o in offers]
    return normalize_cost_criterion(all_co2, target_offer.co2_kg_per_passenger)
