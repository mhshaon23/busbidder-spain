"""
archetypes.py
Predefined traveller profiles for testing and demonstration.
The project asks to show that different travellers get different recommendations:
1. Budget Backpacker (wants lowest price, accepts transfers)
2. Business Executive (wants speed, direct route, flexibility)
3. Flexible Tourist (cares most about ticket flexibility and luggage)
4. Eco-Conscious Traveller (wants lowest CO2 emissions)
"""

from typing import Dict, Any
from src.models.request import TravellerRequest


def create_budget_traveller_request(
    destination: str = "Malaga",
    date_from: str = "2026-07-12",
    date_to: str = "2026-07-14",
    max_budget: float = 45.0,
) -> TravellerRequest:
    """
    Budget Backpacker profile:
    60% weight on price. Willing to take 1 transfer to save money.
    """
    return TravellerRequest(
        destination=destination,
        date_from=date_from,
        date_to=date_to,
        max_budget=max_budget,
        max_transfers=1,
        min_seats=1,
        preferred_departure_window="Morning",
        weights={
            "price": 0.60,
            "duration": 0.15,
            "departure_time": 0.15,
            "flexibility": 0.10,
        }
    )


def create_business_traveller_request(
    destination: str = "Malaga",
    date_from: str = "2026-07-12",
    date_to: str = "2026-07-14",
) -> TravellerRequest:
    """
    Business Executive profile:
    Fast direct route only (0 transfers) and changeable ticket required.
    Duration is 40% of the score.
    """
    return TravellerRequest(
        destination=destination,
        date_from=date_from,
        date_to=date_to,
        max_transfers=0,
        require_changeable=True,
        preferred_departure_window="08:30",
        weights={
            "duration": 0.40,
            "departure_time": 0.30,
            "flexibility": 0.20,
            "price": 0.10,
        }
    )


def create_flexible_tourist_request(
    destination: str = "Malaga",
    date_from: str = "2026-07-12",
    date_to: str = "2026-07-14",
) -> TravellerRequest:
    """
    Flexible Tourist profile:
    Prioritizes refundable/changeable tickets (45% weight) and luggage.
    """
    return TravellerRequest(
        destination=destination,
        date_from=date_from,
        date_to=date_to,
        min_luggage_kg=15,
        preferred_departure_window="Afternoon",
        weights={
            "flexibility": 0.45,
            "customer_rating": 0.20,
            "departure_time": 0.20,
            "price": 0.15,
        }
    )


def create_eco_traveller_request(
    destination: str = "Malaga",
    date_from: str = "2026-07-12",
    date_to: str = "2026-07-14",
) -> TravellerRequest:
    """
    Eco-Conscious Traveller profile:
    50% weight on CO2 emissions (VerdeBus).
    """
    return TravellerRequest(
        destination=destination,
        date_from=date_from,
        date_to=date_to,
        preferred_departure_window="Morning",
        weights={
            "eco_score": 0.50,
            "customer_rating": 0.20,
            "duration": 0.15,
            "price": 0.15,
        }
    )


PROFILES = {
    "budget": ("Budget Backpacker", create_budget_traveller_request),
    "business": ("Business Executive", create_business_traveller_request),
    "flexible": ("Flexible Tourist", create_flexible_tourist_request),
    "eco": ("Eco-Conscious Traveller", create_eco_traveller_request),
}
