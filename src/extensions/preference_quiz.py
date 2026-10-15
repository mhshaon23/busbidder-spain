"""
preference_quiz.py
Optional extension module for qualitative preference elicitation.
Allows travellers to answer a few simple 1-5 questions to automatically
calculate customized ranking weights, rather than typing raw decimals.

Designed as a pluggable extension:
- If this module is imported, the prompt appears during search.
- If the user declines (selects 'n'), search continues normally.
- If this module is omitted, the core system continues without disruption.
"""

from typing import Dict, Optional


def calculate_weights_from_ratings(ratings: Dict[str, float]) -> Dict[str, float]:
    """
    Normalizes a dictionary of 1-5 ratings into weights summing strictly to 1.0.
    Ensures mathematical validity for the RankingEngine.
    """
    # Filter out non-positive ratings and ensure minimum values
    clean_ratings = {k: max(0.5, float(v)) for k, v in ratings.items()}
    total = sum(clean_ratings.values())

    if total == 0:
        # Fallback to balanced equal weights
        n = len(clean_ratings)
        return {k: round(1.0 / n, 4) for k in clean_ratings}

    # Normalize each rating
    raw_weights = {k: v / total for k, v in clean_ratings.items()}

    # Round to 4 decimal places and adjust largest weight to guarantee sum == 1.0000
    rounded_weights = {k: round(v, 4) for k, v in raw_weights.items()}
    current_sum = sum(rounded_weights.values())
    diff = round(1.0 - current_sum, 4)

    if diff != 0:
        # Add difference to the highest weighted criterion
        highest_key = max(rounded_weights, key=rounded_weights.get)
        rounded_weights[highest_key] = round(rounded_weights[highest_key] + diff, 4)

    return rounded_weights


def _ask_rating(question: str, default: int = 3) -> int:
    """Helper to ask a single question with 1 to 5 validation."""
    while True:
        val = input(f"{question} [1-5, Default: {default}]: ").strip()
        if not val:
            return default
        if val.isdigit() and 1 <= int(val) <= 5:
            return int(val)
        print("  Please enter a number between 1 and 5 (or press Enter for default).")


def prompt_preference_quiz() -> Optional[Dict[str, float]]:
    """
    Prompts the user if they want to customize their ranking weights via a quick questionnaire.
    Returns calculated weights dict if user completes quiz, or None if skipped.
    """
    print("\n" + "-" * 70)
    print("OPTIONAL FEATURE: Preference Elicitation")
    choice = input("Would you like to customize your search weights by answering 4 quick questions? (y/n) [Default: n]: ").strip().lower()

    if choice not in ("y", "yes"):
        print("Skipping questionnaire. Using selected profile weights.")
        print("-" * 70)
        return None

    print("\nRate the importance of each factor from 1 (Not important) to 5 (Crucial):")
    
    price_rating = _ask_rating("1. Low Price / Budget savings", default=4)
    speed_rating = _ask_rating("2. Speed / Shortest duration", default=3)
    time_rating = _ask_rating("3. Departure timing (close to preferred time)", default=3)
    flex_rating = _ask_rating("4. Ticket Flexibility (changeable / refundable)", default=2)
    eco_rating = _ask_rating("5. Environmental footprint (low CO2 emissions)", default=2)

    ratings = {
        "price": price_rating,
        "duration": speed_rating,
        "departure_time": time_rating,
        "flexibility": flex_rating,
        "eco_score": eco_rating,
    }

    weights = calculate_weights_from_ratings(ratings)

    print("\n--- Customized Weighting Calculated ---")
    print("Based on your answers, your personalized criteria weights are:")
    for crit, w in weights.items():
        name = crit.replace("_", " ").title()
        print(f"  * {name:<18}: {w * 100:5.1f}%")
    print(f"  * Total Weight      : {sum(weights.values()) * 100:5.1f}%\n" + "-" * 70)

    return weights
