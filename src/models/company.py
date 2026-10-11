"""
Bus company domain model.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Company:
    """Represents a participating bus operator in BusBidder Spain."""
    name: str
    code: str
    profile: str
    default_cancellation_policy: str
    eco_certified: bool = False
