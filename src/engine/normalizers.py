"""
Normalization functions for multi-criteria offer ranking.
Converts heterogeneous physical units (Euros, minutes, ratings, policies) to a standardized 0-100 scale.
"""

from typing import List


def normalize_cost_criterion(values: List[float], val: float) -> float:
    """
    Normalizes a 'lower-is-better' criterion (e.g. price, duration).
    The lowest value receives 100, highest receives 0.
    Handles ties / single-element pools gracefully by awarding 100.
    """
    if not values:
        return 100.0
    min_v = min(values)
    max_v = max(values)
    if abs(max_v - min_v) < 1e-6:
        return 100.0
    # Clamping val between min and max
    clamped_val = max(min_v, min(max_v, val))
    return ((max_v - clamped_val) / (max_v - min_v)) * 100.0


def normalize_benefit_criterion(values: List[float], val: float) -> float:
    """
    Normalizes a 'higher-is-better' criterion (e.g. customer rating, flexibility score).
    The highest value receives 100, lowest receives 0.
    """
    if not values:
        return 100.0
    min_v = min(values)
    max_v = max(values)
    if abs(max_v - min_v) < 1e-6:
        return 100.0
    clamped_val = max(min_v, min(max_v, val))
    return ((clamped_val - min_v) / (max_v - min_v)) * 100.0


def normalize_departure_convenience(departure_hour: float, target_hour: float) -> float:
    """
    Measures circular time proximity on a 24-hour clock.
    The score decreases linearly as the departure time deviates from target_hour.
    A delta of 0 hours gets 100.0; a deviation >= 8 hours gets 0.0.
    """
    # Circular difference on 24-hour dial
    diff = abs(departure_hour - target_hour)
    circular_delta = min(diff, 24.0 - diff)
    
    # 8-hour maximum deviation window
    max_allowed_delta = 8.0
    if circular_delta >= max_allowed_delta:
        return 0.0
    return ((max_allowed_delta - circular_delta) / max_allowed_delta) * 100.0
