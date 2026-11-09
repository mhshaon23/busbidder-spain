"""
extensions package for optional and advanced features in BusBidder Spain.
Demonstrates clean modular architecture where extra features can be added or removed
without breaking core functionality.
"""

from src.extensions.preference_quiz import prompt_preference_quiz, calculate_weights_from_ratings

__all__ = [
    "prompt_preference_quiz",
    "calculate_weights_from_ratings",
]
