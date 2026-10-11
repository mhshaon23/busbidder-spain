"""
Traveller request model.
Distinguishes between hard constraints (filtering) and soft preferences (ranking).
"""

from datetime import date, datetime
from typing import Dict, Optional
from src.validators.exceptions import WeightValidationError, ConstraintViolationError


class TravellerRequest:
    """
    Encapsulates all parameters for a traveller's search query,
    clearly separating non-negotiable hard constraints from soft ranking weights.
    """
    def __init__(
        self,
        destination: str,
        date_from: str,
        date_to: str,
        # Hard Constraints (Filter thresholds)
        max_budget: Optional[float] = None,
        max_transfers: Optional[int] = None,
        max_duration_minutes: Optional[int] = None,
        min_seats: int = 1,
        require_changeable: bool = False,
        require_refundable: bool = False,
        min_luggage_kg: int = 0,
        # Soft Preferences (Ranking weights and target time)
        preferred_departure_window: str = "Morning",  # "Morning", "Afternoon", "Evening", "Night" or "HH:MM"
        weights: Optional[Dict[str, float]] = None,
    ):
        self.destination = destination.strip()
        self.date_from = datetime.strptime(date_from.strip(), "%Y-%m-%d").date()
        self.date_to = datetime.strptime(date_to.strip(), "%Y-%m-%d").date()

        if self.date_to < self.date_from:
            raise ConstraintViolationError(
                f"Invalid travel window: end date ({date_to}) cannot precede start date ({date_from})."
            )

        # Hard constraints
        self.max_budget = float(max_budget) if max_budget is not None else None
        self.max_transfers = int(max_transfers) if max_transfers is not None else None
        self.max_duration_minutes = int(max_duration_minutes) if max_duration_minutes is not None else None
        self.min_seats = max(1, int(min_seats))
        self.require_changeable = bool(require_changeable)
        self.require_refundable = bool(require_refundable)
        self.min_luggage_kg = int(min_luggage_kg)

        # Soft preferences
        self.preferred_departure_window = preferred_departure_window.strip()
        
        # Default balanced weights if none provided
        self.weights = weights or {
            "price": 0.40,
            "duration": 0.25,
            "departure_time": 0.15,
            "flexibility": 0.20,
        }
        self.validate_weights()

    def validate_weights(self) -> None:
        """Ensures all weights are non-negative and sum to 1.0 (with small floating tolerance)."""
        total = sum(self.weights.values())
        if any(w < 0 for w in self.weights.values()):
            raise WeightValidationError("Criteria weights cannot be negative.")
        if not (0.999 <= total <= 1.001):
            raise WeightValidationError(f"Criteria weights must sum to 1.0 (100%), got {total:.4f}.")

    @property
    def target_hour(self) -> float:
        """
        Converts the preferred departure window or explicit time into an hour float [0.0 - 24.0]
        used for distance-based departure time scoring.
        """
        window_lower = self.preferred_departure_window.lower()
        if "morn" in window_lower:
            return 9.0   # 09:00
        elif "afternoon" in window_lower:
            return 14.0  # 14:00
        elif "even" in window_lower:
            return 19.0  # 19:00
        elif "night" in window_lower:
            return 23.5  # 23:30
        
        # Check if an explicit HH:MM was passed
        try:
            t = datetime.strptime(self.preferred_departure_window, "%H:%M")
            return t.hour + t.minute / 60.0
        except ValueError:
            return 10.0  # fallback to mid-morning
