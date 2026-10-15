"""
BusBidder Spain - Main Entry Point.
Fulfills all requirements for command-line execution and demonstration.
"""

import sys
import argparse
from typing import Optional

from src.loaders.data_loader import DataLoader
from src.engine.filters import FilterEngine
from src.engine.ranker import RankingEngine
from src.engine.explainer import RecommendationExplainer
from src.booking.manager import BookingManager
from src.models.request import TravellerRequest
from src.profiles.archetypes import PROFILES
from src.cli.interface import (
    print_banner,
    display_ranked_offers_table,
    display_criteria_breakdown_table,
    run_demonstration,
)

# Optional Extension: Pluggable Preference Quiz module
try:
    from src.extensions.preference_quiz import prompt_preference_quiz
    HAS_PREFERENCE_QUIZ = True
except ImportError:
    HAS_PREFERENCE_QUIZ = False


def interactive_session():
    """Interactive loop for searching, ranking, and booking bus journeys."""
    print_banner()
    loader = DataLoader()
    offers, quarantined = loader.load_offers()
    destinations = loader.load_destinations()
    booking_manager = BookingManager()
    filter_engine = FilterEngine()
    ranker = RankingEngine()

    dest_list = sorted(list(destinations.keys()))
    print("\nAvailable destinations from Madrid:")
    for idx, d in enumerate(dest_list, start=1):
        print(f"  [{idx:2d}] {d:<24}", end="" if idx % 3 != 0 else "\n")
    print("\n")

    # 1. Destination selection
    choice = input("Enter destination name or number [Default: Malaga]: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(dest_list):
        dest_name = dest_list[int(choice) - 1]
    elif choice in destinations:
        dest_name = choice
    else:
        dest_name = "Malaga"

    print(f"Selected destination: {dest_name}")

    # 2. Date selection
    d_from = input("Travel start date (YYYY-MM-DD) [Default: 2026-07-12]: ").strip() or "2026-07-12"
    d_to = input("Travel end date (YYYY-MM-DD) [Default: 2026-07-14]: ").strip() or "2026-07-14"

    # 3. Traveller Profile selection
    print("\nChoose Traveller Archetype:")
    print("  [1] Budget Backpacker (Maximize savings, price weight 60%)")
    print("  [2] Business Executive (Speed, 0 transfers, prime schedule)")
    print("  [3] Flexible Tourist (High refundability, generous luggage)")
    print("  [4] Eco-Conscious Traveller (Lowest CO2 emissions)")
    p_choice = input("Select profile [1-4, Default: 1]: ").strip() or "1"

    if p_choice == "2":
        profile_key = "business"
    elif p_choice == "3":
        profile_key = "flexible"
    elif p_choice == "4":
        profile_key = "eco"
    else:
        profile_key = "budget"

    profile_name, profile_func = PROFILES[profile_key]
    req: TravellerRequest = profile_func(destination=dest_name, date_from=d_from, date_to=d_to)

    # Optional Feature: Offer customized weight elicitation quiz if extension is enabled
    if HAS_PREFERENCE_QUIZ:
        custom_weights = prompt_preference_quiz()
        if custom_weights:
            req.weights = custom_weights
            req.validate_weights()

    print(f"\nApplied Profile: {profile_name if not (HAS_PREFERENCE_QUIZ and custom_weights) else 'Custom Questionnaire'}")
    print(f"Configured Weights: {req.weights}")

    # 4. Filter offers
    filter_result = filter_engine.filter_offers(offers, req)
    print(f"\n--- Filter Results ---")
    print(f"Initial offers considered : {filter_result.total_initial}")
    print(f"Offers passing constraints: {len(filter_result.accepted_offers)} ({filter_result.survival_rate:.1f}%)")
    
    if not filter_result.accepted_offers:
        print("No offers matched your constraints. Try widening your budget or date window.")
        return

    # 5. Rank offers
    ranked_offers = ranker.rank_offers(filter_result.accepted_offers, req)
    print("\n")
    display_ranked_offers_table(ranked_offers, limit=8)
    display_criteria_breakdown_table(ranked_offers, limit=5)

    # 6. Show Explainable Recommendation
    explanation = RecommendationExplainer.explain_top_offer(ranked_offers, req)
    print("\n" + "=" * 70)
    print(explanation)
    print("=" * 70 + "\n")

    # 7. Booking Simulation
    book_opt = input("Would you like to book an offer? (y/n) [Default: y]: ").strip().lower()
    if book_opt in ("", "y", "yes"):
        rank_str = input(f"Enter rank to book (1-{len(ranked_offers)}) [Default: 1]: ").strip() or "1"
        try:
            chosen_rank = int(rank_str)
            target_ro = next(ro for ro in ranked_offers if ro.rank == chosen_rank)
        except (ValueError, StopIteration):
            print("Invalid rank selected. Defaulting to Rank #1.")
            target_ro = ranked_offers[0]

        passenger_name = input("Enter traveller full name [Default: Alex Smith]: ").strip() or "Alex Smith"
        seats_str = input("Number of seats [Default: 1]: ").strip() or "1"
        seats_num = int(seats_str) if seats_str.isdigit() else 1

        try:
            record = booking_manager.create_booking(target_ro.offer, passenger_name=passenger_name, seats=seats_num)
            print("\nBooking successfully generated and persisted!\n")
            print(record.generate_ticket())
        except Exception as e:
            print(f"\nBooking failed: {e}\n")


def show_quarantine():
    """Displays data records currently in quarantine review."""
    loader = DataLoader()
    _, quarantined = loader.load_offers()
    print_banner()
    print(f"\n[QUARANTINE REVIEW] Inspecting invalid records...")
    if not quarantined:
        print("No quarantined records found in standard catalogue.")
        # Try loading sample corrupt file
        corrupt_path = loader.data_dir / "corrupt_offers_sample.csv"
        if corrupt_path.exists():
            print(f"Loading test corrupt file: {corrupt_path.name}")
            _, sample_q = loader.load_offers(file_path=corrupt_path)
            for idx, item in enumerate(sample_q, start=1):
                print(f"  {idx}. Line {item.get('line_number')}: ID {item.get('offer_id')} -> Reason: {item.get('rejection_reason')}")
    else:
        for idx, item in enumerate(quarantined, start=1):
            print(f"  {idx}. Line {item.get('line_number')}: ID {item.get('offer_id')} -> Reason: {item.get('rejection_reason')}")


def main():
    parser = argparse.ArgumentParser(description="BusBidder Spain - Multi-Criteria Booking & Ranking Platform")
    parser.add_argument("--demo", action="store_true", help="Run automated sensitivity demonstration comparing all 4 traveller profiles")
    parser.add_argument("--interactive", action="store_true", help="Run interactive search, ranking, and booking prompt")
    parser.add_argument("--quarantine", action="store_true", help="Inspect quarantined corrupt records and rejection reasons")

    args = parser.parse_args()

    if args.demo:
        run_demonstration()
    elif args.quarantine:
        show_quarantine()
    elif args.interactive:
        interactive_session()
    else:
        # Default: run demo and then prompt
        run_demonstration()


if __name__ == "__main__":
    main()

