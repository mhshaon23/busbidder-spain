"""
User interface and presentation module for BusBidder Spain.
Provides both rich formatted tables and clear command-line navigation.
"""

from typing import List, Optional
from src.loaders.data_loader import DataLoader
from src.models.offer import Offer
from src.models.request import TravellerRequest
from src.engine.filters import FilterEngine, FilterResult
from src.engine.ranker import RankingEngine, RankedOffer
from src.engine.explainer import RecommendationExplainer
from src.booking.manager import BookingManager
from src.profiles.archetypes import (
    PROFILES,
    create_budget_traveller_request,
    create_business_traveller_request,
    create_flexible_tourist_request,
    create_eco_traveller_request,
)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False


def print_banner():
    title = (
        "=========================================================================\n"
        "                  BUSBIDDER SPAIN - TRAVEL PLATFORM                      \n"
        "       Flexible Bus-Booking & Multi-Criteria Offer-Ranking Engine        \n"
        "                     OsloMet ACIT4420 Project 2026                       \n"
        "========================================================================="
    )
    if HAS_RICH:
        console.print(Panel(title, style="bold cyan", border_style="bright_blue"))
    else:
        print(title)


def display_ranked_offers_table(ranked_offers: List[RankedOffer], limit: int = 10):
    if not ranked_offers:
        print("\nNo offers met the specified criteria.\n")
        return

    if HAS_RICH:
        table = Table(
            title=f"Top {min(len(ranked_offers), limit)} Ranked Offers",
            box=box.ROUNDED,
            header_style="bold magenta",
        )
        table.add_column("Rank", justify="center", style="bold yellow", width=5)
        table.add_column("Offer ID", justify="center", width=12)
        table.add_column("Company", style="green", width=15)
        table.add_column("Depart", justify="center", width=7)
        table.add_column("Arrive", justify="center", width=7)
        table.add_column("Duration", justify="right", width=9)
        table.add_column("Price (EUR)", justify="right", style="bold cyan", width=11)
        table.add_column("Flex", justify="center", width=8)
        table.add_column("CO2 (kg)", justify="right", width=8)
        table.add_column("Seats", justify="center", width=6)
        table.add_column("Score", justify="right", style="bold red", width=7)

        for ro in ranked_offers[:limit]:
            o = ro.offer
            flex_str = "Full" if (o.is_changeable and o.is_refundable) else ("Change" if o.is_changeable else "Strict")
            dur_hours = int(o.duration_minutes // 60)
            dur_mins = int(o.duration_minutes % 60)
            dur_str = f"{dur_hours}h {dur_mins:02d}m"
            table.add_row(
                str(ro.rank),
                o.offer_id,
                o.company,
                o.departure_time_str,
                o.arrival_time_str,
                dur_str,
                f"EUR {o.price:.2f}",
                flex_str,
                f"{o.co2_kg_per_passenger:.1f}",
                str(o.available_seats),
                f"{ro.weighted_total_score:.1f}",
            )
        console.print(table)
    else:
        print(f"\n--- Top {min(len(ranked_offers), limit)} Ranked Offers ---")
        print(f"{'Rank':<5} {'ID':<15} {'Company':<16} {'Depart':<8} {'Duration':<10} {'Price':<10} {'Score':<8}")
        for ro in ranked_offers[:limit]:
            o = ro.offer
            dur_str = f"{o.duration_minutes // 60}h {o.duration_minutes % 60}m"
            print(f"{ro.rank:<5} {o.offer_id:<15} {o.company:<16} {o.departure_time_str:<8} {dur_str:<10} €{o.price:<8.2f} {ro.weighted_total_score:<8.1f}")


def display_criteria_breakdown_table(ranked_offers: List[RankedOffer], limit: int = 5):
    if not ranked_offers:
        return

    active_criteria = list(ranked_offers[0].criterion_scores.keys())

    if HAS_RICH:
        table = Table(
            title="Normalized Component Scores Breakdown (0 - 100 Scale)",
            box=box.SIMPLE_HEAD,
            header_style="bold blue",
        )
        table.add_column("Rank", justify="center", width=5)
        table.add_column("Offer ID", justify="center", width=12)
        table.add_column("Company", width=15)
        for crit in active_criteria:
            table.add_column(f"{crit.replace('_', ' ').title()}", justify="right")
        table.add_column("Total Score", justify="right", style="bold red")

        for ro in ranked_offers[:limit]:
            scores = ro.criterion_scores
            row_vals = [str(ro.rank), ro.offer.offer_id, ro.offer.company]
            for crit in active_criteria:
                row_vals.append(f"{scores.get(crit, 0):.1f}")
            row_vals.append(f"{ro.weighted_total_score:.1f}")
            table.add_row(*row_vals)
        console.print(table)


def run_demonstration():
    """
    Executes a multi-profile sensitivity demonstration on Madrid -> Malaga,
    showing how Budget, Business, and Eco profiles produce distinct recommendations.
    """
    print_banner()
    loader = DataLoader()
    offers, _ = loader.load_offers()
    destinations = loader.load_destinations()
    filter_engine = FilterEngine()
    ranker = RankingEngine()

    dest = "Malaga"
    d_from = "2026-07-12"
    d_to = "2026-07-14"

    profiles_to_run = [
        ("Budget Backpacker", create_budget_traveller_request(dest, d_from, d_to, max_budget=45.0)),
        ("Business Executive", create_business_traveller_request(dest, d_from, d_to)),
        ("Eco-Conscious Traveller", create_eco_traveller_request(dest, d_from, d_to)),
        ("Flexible Tourist", create_flexible_tourist_request(dest, d_from, d_to)),
    ]

    for p_name, req in profiles_to_run:
        print("\n" + "=" * 75)
        print(f" DEMONSTRATION PROFILE: {p_name.upper()}")
        print("=" * 75)
        print(f"Constraints: Destination={req.destination}, Dates={req.date_from} to {req.date_to}, "
              f"MaxBudget={req.max_budget}, DirectOnly={req.max_transfers==0}")
        print(f"Weights    : {req.weights}")

        f_result = filter_engine.filter_offers(offers, req)
        print(f"\nFiltering Result: {len(f_result.accepted_offers)} acceptable offers "
              f"(Survival rate: {f_result.survival_rate:.1f}%)")
        print(f"Rejections breakdown: {dict((k, v) for k, v in f_result.rejection_counts.items() if v > 0)}")

        ranked = ranker.rank_offers(f_result.accepted_offers, req)
        display_ranked_offers_table(ranked, limit=5)
        display_criteria_breakdown_table(ranked, limit=3)

        explanation = RecommendationExplainer.explain_top_offer(ranked, req)
        if HAS_RICH:
            console.print(Panel(explanation, title="Explainable Recommendation", border_style="yellow"))
        else:
            print("\n" + explanation)
