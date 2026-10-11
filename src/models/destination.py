"""
Destination domain model.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Destination:
    """Represents a travel destination from Madrid hub."""
    name: str
    distance_km: int
    region: str
    is_coastal: bool

    def __post_init__(self) -> None:
        if self.distance_km <= 0:
            raise ValueError(f"Distance for destination '{self.name}' must be positive.")
