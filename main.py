"""
BusBidder Spain - Main Entry Point.
Fulfills all requirements for command-line execution and demonstration.
Features robust input validation that re-prompts on incorrect values.
"""

import sys
import argparse
from datetime import datetime
from typing import Optional

from src.loaders.data_loader import DataLoader
from src.engine.filters import FilterEngine
from src.engine.ranker import RankingEngine
from src.engine.explainer import RecommendationExplainer
from src.booking.manager import BookingManager
from src.models.request import TravellerRequest
from src.profiles.archetypes import PROFILES
from src.validators.regex_patterns import is_valid_date
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
    """Interactive loop for searching, ranking, and booking bus journeys with strict validation."""
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

    # 1. Destination selection with strict validation
    while True:
        choice = input("Enter destination name or number [Default: Malaga]: ").strip()
        if not choice:
            dest_name = "Malaga"
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(dest_list):
            dest_name = dest_list[int(choice) - 1]
            break
        else:
            # Case-insensitive name match
            matched = [d for d in dest_list if d.lower() == choice.lower()]
            if matched:
                dest_name = matched[0]
                break
            print(f"  Error: Unknown destination '{choice}'. Please enter a number (1-{len(dest_list)}) or a city name from the list above.")

    print(f"Selected destination: {dest_name}")

    # 2. Date selection with validation
    while True:
        d_from = input("Travel start date (YYYY-MM-DD) [Default: 2026-07-12]: ").strip() or "2026-07-12"
        if is_valid_date(d_from):
            break
        print(f"  Error: Invalid date format '{d_from}'. Please use YYYY-MM-DD (e.g. 2026-07-12).")

    while True:
        d_to = input("Travel end date (YYYY-MM-DD) [Default: 2026-07-14]: ").strip() or "2026-07-14"
        if not is_valid_date(d_to):
            print(f"  Error: Invalid date format '{d_to}'. Please use YYYY-MM-DD (e.g. 2026-07-14).")
            continue
        # Verify logical date order
        dt_start = datetime.strptime(d_from, "%Y-%m-%d").date()
        dt_end = datetime.strptime(d_to, "%Y-%m-%d").date()
        if dt_end < dt_start:
            print(f"  Error: Travel end date ({d_to}) cannot be earlier than start date ({d_from}).")
            continue
        break

    # 3. Preference Elicitation (Customization) or Preset Archetypes
    custom_weights = None
    if HAS_PREFERENCE_QUIZ:
        custom_weights = prompt_preference_quiz()

    if custom_weights:
        # User completed the questionnaire: use custom weights directly (no 4 presets asked)
        req: TravellerRequest = TravellerRequest(
            destination=dest_name,
            date_from=d_from,
            date_to=d_to,
            weights=custom_weights,
        )
        profile_name = "Custom Questionnaire"
    else:
        # User declined customization: show the 4 preset traveller archetypes
        print("\nChoose Traveller Archetype:")
        print("  [1] Budget Backpacker (Price is given more priority, accepts transfers to save money)")
        print("  [2] Business Executive (Fastest direct travel and departure time are given priority)")
        print("  [3] Flexible Tourist (Ticket changes, refunds, and luggage are given priority)")
        print("  [4] Eco-Conscious Traveller (Lowest CO2 emissions and green transport are given priority)")

        while True:
            p_choice = input("Select profile [1-4, Default: 1]: ").strip() or "1"
            if p_choice in ("1", "2", "3", "4"):
                break
            print(f"  Error: Invalid selection '{p_choice}'. Please enter a number from 1 to 4.")

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

    print(f"\nApplied Profile: {profile_name}")
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

    # 7. Booking Simulation with strict input validation
    while True:
        book_opt = input("Would you like to book an offer? (y/n) [Default: y]: ").strip().lower()
        if book_opt in ("", "y", "yes", "n", "no"):
            break
        print(f"  Error: Invalid response '{book_opt}'. Please enter 'y' for yes or 'n' for no.")

    if book_opt in ("", "y", "yes"):
        while True:
            rank_str = input(f"Enter rank to book (1-{len(ranked_offers)}) [Default: 1]: ").strip() or "1"
            if rank_str.isdigit() and 1 <= int(rank_str) <= len(ranked_offers):
                chosen_rank = int(rank_str)
                target_ro = next(ro for ro in ranked_offers if ro.rank == chosen_rank)
                break
            print(f"  Error: Invalid rank '{rank_str}'. Please enter a whole number between 1 and {len(ranked_offers)}.")

        passenger_name = input("Enter traveller full name [Default: Alex Smith]: ").strip() or "Alex Smith"

        while True:
            seats_str = input(f"Number of seats (1-{target_ro.offer.available_seats}) [Default: 1]: ").strip() or "1"
            if seats_str.isdigit() and int(seats_str) >= 1:
                seats_num = int(seats_str)
                if seats_num <= target_ro.offer.available_seats:
                    break
                print(f"  Error: Cannot book {seats_num} seat(s). Only {target_ro.offer.available_seats} seat(s) available on this bus.")
            else:
                print("  Error: Please enter a positive whole number of seats.")

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
        # Default: run demo
        run_demonstration()


if __name__ == "__main__":
    main()
