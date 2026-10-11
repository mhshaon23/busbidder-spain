"""
Predefined traveller profiles for sensitivity analysis and demonstration.
Directly satisfies Section 6 requirement: 'Support different traveller profiles'.
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
    Profile: Budget Backpacker
    Prioritizes low cost above all other parameters. Accepts transfers and strict fares.
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
    Profile: Business Executive
    Prioritizes speed, convenience, and schedule certainty. Price is secondary.
    Strictly forbids transfers.
    """
    return TravellerRequest(
        destination=destination,
        date_from=date_from,
        date_to=date_to,
        max_transfers=0,  # Direct only
        require_changeable=True,  # Mandatory flexibility
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
    Profile: Flexibility-Focused Tourist
    Prioritizes free ticket alterations, refundability, and generous luggage.
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
    Profile: Eco-Conscious Traveller
    Prioritizes lowest environmental footprint (CO2 per passenger).
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
