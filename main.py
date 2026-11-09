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
from src.validators.regex_patterns import is_valid_date, is_valid_time
from src.validators.exceptions import BusBidderError
from src.cli.interface import (
    print_banner,
    display_ranked_offers_table,
    display_criteria_breakdown_table,
    describe_request,
    run_demonstration,
)

# Optional Extension: Pluggable Preference Quiz module
try:
    from src.extensions.preference_quiz import prompt_preference_quiz
    HAS_PREFERENCE_QUIZ = True
except ImportError:
    HAS_PREFERENCE_QUIZ = False


def ask_optional_number(prompt: str, cast=float, min_value: float = 0) -> Optional[float]:
    """Asks for a number; Enter means 'no limit' (None). Re-prompts on invalid input."""
    while True:
        raw = input(f"{prompt} [Enter = no limit]: ").strip().replace(",", ".")
        if not raw:
            return None
        try:
            value = cast(raw)
        except ValueError:
            print(f"  Error: '{raw}' is not a valid number. Please try again or press Enter for no limit.")
            continue
        if value < min_value:
            print(f"  Error: Value must be at least {min_value}.")
            continue
        return value


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """Asks a y/n question with a default. Re-prompts on invalid input."""
    default_str = "y" if default else "n"
    while True:
        raw = input(f"{prompt} (y/n) [Default: {default_str}]: ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print(f"  Error: Invalid response '{raw}'. Please enter 'y' for yes or 'n' for no.")


def ask_departure_preference() -> Optional[str]:
    """Asks for a preferred departure as a part of day or an exact HH:MM time."""
    while True:
        raw = input("Preferred departure (Morning/Afternoon/Evening/Night or HH:MM) [Enter = profile default]: ").strip()
        if not raw:
            return None
        if raw.lower() in ("morning", "afternoon", "evening", "night"):
            return raw.capitalize()
        if is_valid_time(raw):
            return raw
        print(f"  Error: '{raw}' is not recognised. Use Morning, Afternoon, Evening, Night or a time like 08:30.")


def apply_user_constraints(req: TravellerRequest, limits: dict) -> None:
    """
    Combines the traveller's own hard constraints with those of the chosen profile.
    The stricter value always wins, so a profile can never loosen a traveller's limit.
    """
    if limits["max_budget"] is not None:
        req.max_budget = min(limits["max_budget"], req.max_budget) if req.max_budget is not None else limits["max_budget"]
    if limits["max_transfers"] is not None:
        req.max_transfers = min(limits["max_transfers"], req.max_transfers) if req.max_transfers is not None else limits["max_transfers"]
    if limits["max_duration_minutes"] is not None:
        req.max_duration_minutes = (
            min(limits["max_duration_minutes"], req.max_duration_minutes)
            if req.max_duration_minutes is not None else limits["max_duration_minutes"]
        )
    req.min_luggage_kg = max(req.min_luggage_kg, limits["min_luggage_kg"])
    req.require_changeable = req.require_changeable or limits["require_changeable"]
    req.require_refundable = req.require_refundable or limits["require_refundable"]
    if limits["preferred_departure"]:
        req.preferred_departure_window = limits["preferred_departure"]


def interactive_session():
    """Interactive loop for searching, ranking, and booking bus journeys with strict validation."""
    print_banner()
    loader = DataLoader()
    offers, quarantined = loader.load_offers()
    destinations = loader.load_destinations()
    booking_manager = BookingManager()
    # Seats already sold in earlier sessions are deducted so capacity stays consistent
    booking_manager.apply_existing_bookings(offers)
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

    # 3. Hard constraints chosen by the traveller (offers that break them are removed)
    print("\n--- Hard constraints: offers that break these are REMOVED before ranking ---")
    max_duration_hours = ask_optional_number("Maximum journey duration in hours", float, 0.5)
    limits = {
        "max_budget": ask_optional_number("Maximum price per seat in EUR", float, 1),
        "max_transfers": ask_optional_number("Maximum number of transfers", int, 0),
        "max_duration_minutes": int(max_duration_hours * 60) if max_duration_hours is not None else None,
        "min_luggage_kg": int(ask_optional_number("Minimum luggage allowance in kg", int, 0) or 0),
        "require_changeable": ask_yes_no("Must the ticket be changeable?", default=False),
        "require_refundable": ask_yes_no("Must the ticket be refundable?", default=False),
    }

    # Soft preference that is not a weight: the preferred departure time
    print("\n--- Soft preferences: these only change the ORDER of the remaining offers ---")
    limits["preferred_departure"] = ask_departure_preference()

    # 4. Preference Elicitation (Customization) or Preset Archetypes
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
        # User declined customization: show the preset traveller profiles
        print("\nChoose Traveller Profile:")
        print("  [1] Budget Backpacker (Price is given more priority, accepts transfers to save money)")
        print("  [2] Business Executive (Fastest direct travel and departure time are given priority)")
        print("  [3] Flexible Tourist (Ticket changes, refunds, and luggage are given priority)")
        print("  [4] Eco-Conscious Traveller (Lowest CO2 emissions and green transport are given priority)")
        print("  [5] Balanced (price, duration, departure time and flexibility all count, price the most)")

        profile_keys = {"1": "budget", "2": "business", "3": "flexible", "4": "eco", "5": "balanced"}
        while True:
            p_choice = input("Select profile [1-5, Default: 1]: ").strip() or "1"
            if p_choice in profile_keys:
                break
            print(f"  Error: Invalid selection '{p_choice}'. Please enter a number from 1 to 5.")

        profile_key = profile_keys[p_choice]

        profile_name, profile_func = PROFILES[profile_key]
        req: TravellerRequest = profile_func(destination=dest_name, date_from=d_from, date_to=d_to)

    apply_user_constraints(req, limits)

    print(f"\nApplied Profile: {profile_name}")
    print(describe_request(req))

    # 5. Filter offers
    filter_result = filter_engine.filter_offers(offers, req)
    print(f"\n--- Filter Results ---")
    print(f"Initial offers considered : {filter_result.total_initial}")
    print(f"Offers passing constraints: {len(filter_result.accepted_offers)} ({filter_result.survival_rate:.1f}%)")
    removed = {k: v for k, v in filter_result.rejection_counts.items() if v > 0}
    print(f"Offers removed, by first broken constraint: {removed}")

    if not filter_result.accepted_offers:
        print("No offers matched your constraints. Try widening your budget or date window.")
        return

    # 6. Rank offers
    ranked_offers = ranker.rank_offers(filter_result.accepted_offers, req)
    print("\n")
    display_ranked_offers_table(ranked_offers, limit=8)
    display_criteria_breakdown_table(ranked_offers, limit=5)

    # 7. Show Explainable Recommendation
    explanation = RecommendationExplainer.explain_top_offer(ranked_offers, req)
    print("\n" + "=" * 70)
    print(explanation)
    print("=" * 70 + "\n")

    # 8. Booking Simulation with strict input validation
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

    # Known application errors (missing data files, invalid weights, booking problems)
    # are shown as a short message instead of a Python traceback.
    try:
        if args.quarantine:
            show_quarantine()
        elif args.interactive:
            interactive_session()
        else:
            # --demo, and also the default when no option is given
            run_demonstration()
    except BusBidderError as err:
        print(f"\nError: {err}")
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\nSession ended by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
