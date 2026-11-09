"""
normalizers.py
Functions to normalize different criteria to a standard 0 to 100 scale.
In this project, we have to compare things with totally different units:
- Price is in Euros (lower is better)
- Duration is in minutes (lower is better)
- Customer rating is 1.0 to 5.0 (higher is better)
- Flexibility is a score from 0.0 to 1.0 (higher is better)
- Departure time is compared to preferred time on a 24h clock

Min-Max normalization formula:
- Lower is better (cost):    ((max - val) / (max - min)) * 100
- Higher is better (benefit): ((val - min) / (max - min)) * 100
"""

from typing import List


def normalize_cost_criterion(values: List[float], val: float) -> float:
    """
    Normalizes a criterion where lower is better (e.g. price, duration).
    The best (lowest) value gets 100, and the worst (highest) gets 0.
    If all offers have the same value, they all get 100.
    """
    if not values:
        return 100.0
    min_v = min(values)
    max_v = max(values)
    
    # Avoid division by zero if all values are equal
    if abs(max_v - min_v) < 1e-6:
        return 100.0

    # Clamp value just in case it is outside min/max range
    clamped_val = max(min_v, min(max_v, val))
    return ((max_v - clamped_val) / (max_v - min_v)) * 100.0


def normalize_benefit_criterion(values: List[float], val: float) -> float:
    """
    Normalizes a criterion where higher is better (e.g. rating, flexibility).
    The best (highest) value gets 100, and the worst (lowest) gets 0.
    """
    if not values:
        return 100.0
    min_v = min(values)
    max_v = max(values)

    # Avoid division by zero
    if abs(max_v - min_v) < 1e-6:
        return 100.0

    clamped_val = max(min_v, min(max_v, val))
    return ((clamped_val - min_v) / (max_v - min_v)) * 100.0


def normalize_departure_convenience(departure_hour: float, target_hour: float) -> float:
    """
    Calculates how close the departure time is to the user's preferred time.
    Uses circular clock distance so 23:00 and 01:00 are only 2 hours apart.
    - If right on time (diff = 0 hours): gets 100.0
    - If 8 or more hours away: gets 0.0
    """
    diff = abs(departure_hour - target_hour)
    circular_delta = min(diff, 24.0 - diff)
    
    max_allowed_delta = 8.0
    if circular_delta >= max_allowed_delta:
        return 0.0
    return ((max_allowed_delta - circular_delta) / max_allowed_delta) * 100.0
