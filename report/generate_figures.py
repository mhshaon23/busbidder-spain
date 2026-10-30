"""
generate_figures.py
Generates visual diagrams and charts for the ACIT4420 final report using matplotlib.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure report output directory exists
OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)


def create_architecture_diagram():
    """Generates the system architecture and information flow diagram."""
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Style definitions
    box_style_data = dict(boxstyle="round,pad=0.5", facecolor="#E3F2FD", edgecolor="#1976D2", linewidth=1.5)
    box_style_proc = dict(boxstyle="round,pad=0.5", facecolor="#E8F5E9", edgecolor="#388E3C", linewidth=1.5)
    box_style_eval = dict(boxstyle="round,pad=0.5", facecolor="#FFF3E0", edgecolor="#F57C00", linewidth=1.5)
    box_style_sink = dict(boxstyle="round,pad=0.5", facecolor="#F3E5F5", edgecolor="#7B1FA2", linewidth=1.5)

    # 1. Data Ingestion Layer
    ax.text(2, 6.8, "Storage Layer\n• offers.csv (225 rows)\n• companies.json (5)\n• destinations.json (15)", 
            ha="center", va="center", bbox=box_style_data, fontsize=9, fontweight="bold")
    
    ax.text(2, 4.2, "Data Ingestion & Validation\n(DataLoader)\n• Descriptors (bounds/types)\n• Regex (ID patterns)\n• Relational foreign checks", 
            ha="center", va="center", bbox=box_style_proc, fontsize=9)

    ax.text(2, 1.5, "Audit & Quarantine Sink\n• quarantine_offers.csv\n• busbidder.log", 
            ha="center", va="center", bbox=box_style_sink, fontsize=9)

    # 2. Decision Core Layer
    ax.text(6, 6.8, "User Request & Constraints\n(TravellerRequest)\n• Hard Constraints (budget, dates)\n• Soft Preferences (weights)\n• Optional Preference Quiz", 
            ha="center", va="center", bbox=box_style_data, fontsize=9, fontweight="bold")

    ax.text(6, 4.2, "Hard Constraint Filtering\n(FilterEngine)\n• Removes unacceptable offers\n• Records audit rejection causes\n• Computes survival rate %", 
            ha="center", va="center", bbox=box_style_proc, fontsize=9)

    ax.text(6, 1.5, "Multi-Criteria Decision Engine\n• Normalizers (0-100 scale)\n• @register_criterion Registry\n• Weighted Sum Total Score", 
            ha="center", va="center", bbox=box_style_eval, fontsize=9, fontweight="bold")

    # 3. Output & Booking Layer
    ax.text(10, 6.8, "Simulated Booking Store\n• bookings.json (ledger)\n• Unique ES-XXXXXX code\n• Seats re-applied on restart", 
            ha="center", va="center", bbox=box_style_sink, fontsize=9, fontweight="bold")

    ax.text(10, 4.2, "Recommendation & Explanation\n(RecommendationExplainer)\n• Ranked table & scores\n• Contrastive pros & trade-offs\n• Transparent non-objective note", 
            ha="center", va="center", bbox=box_style_proc, fontsize=9)

    ax.text(10, 1.5, "Interactive Interface\n(CLI & Terminal Tables)\n• Rich / ASCII tabular views\n• Ticket receipt generation", 
            ha="center", va="center", bbox=box_style_data, fontsize=9)

    # Connecting Arrows
    arrow_props = dict(arrowstyle="->", color="#37474F", lw=1.5, mutation_scale=15)
    
    # Storage -> Loader
    ax.annotate("", xy=(2, 5.2), xytext=(2, 5.8), arrowprops=arrow_props)
    # Loader -> Quarantine
    ax.annotate("Invalid\nRows", xy=(2, 2.3), xytext=(2, 3.2), ha="center", fontsize=8, color="#C62828", arrowprops=dict(arrowstyle="->", color="#C62828", lw=1.2))
    # Loader -> Filter
    ax.annotate("Valid\nOffers", xy=(4.6, 4.2), xytext=(3.4, 4.2), arrowprops=arrow_props)
    # Request -> Filter
    ax.annotate("", xy=(6, 5.2), xytext=(6, 5.8), arrowprops=arrow_props)
    # Filter -> Scoring
    ax.annotate("Surviving\nOffers", xy=(6, 2.5), xytext=(6, 3.2), arrowprops=arrow_props)
    # Scoring -> Explainer
    ax.annotate("", xy=(8.8, 4.2), xytext=(7.4, 2.3), arrowprops=arrow_props)
    # Explainer -> Interface
    ax.annotate("", xy=(10, 2.3), xytext=(10, 3.2), arrowprops=arrow_props)
    # Interface -> Booking
    ax.annotate("Book\nOffer", xy=(10, 5.8), xytext=(10, 5.2), arrowprops=arrow_props)

    plt.title("BusBidder Spain — Component Architecture & Decision Pipeline", fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    out_path = OUT_DIR / "architecture_diagram.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def compute_profile_winners():
    """Runs the four demo profiles on Madrid -> Malaga (12-14 July) and returns each winner."""
    import sys
    sys.path.insert(0, str(OUT_DIR.parent))
    from src.loaders.data_loader import DataLoader
    from src.engine.filters import FilterEngine
    from src.engine.ranker import RankingEngine
    from src.profiles.archetypes import (
        create_budget_traveller_request,
        create_business_traveller_request,
        create_eco_traveller_request,
        create_flexible_tourist_request,
    )

    offers, _ = DataLoader().load_offers()
    requests = [
        ("Budget\nBackpacker", create_budget_traveller_request(max_budget=45.0)),
        ("Business\nExecutive", create_business_traveller_request()),
        ("Eco-Conscious\nTraveller", create_eco_traveller_request()),
        ("Flexible\nTourist", create_flexible_tourist_request()),
    ]
    winners = []
    for label, req in requests:
        accepted = FilterEngine().filter_offers(offers, req).accepted_offers
        top = RankingEngine().rank_offers(accepted, req)[0]
        winners.append({
            "label": label,
            "company": f"{top.offer.company}\n{top.offer.offer_id}",
            "score": round(top.weighted_total_score, 1),
            "price": top.offer.price,
        })
    return winners


def create_profile_comparison_chart():
    """Generates a comparison bar chart illustrating sensitivity across traveller profiles."""
    # Values come from the live ranking engine (not typed in by hand),
    # so the chart always matches what `python main.py --demo` prints.
    winners = compute_profile_winners()
    profiles = [w["label"] for w in winners]
    companies = [w["company"] for w in winners]
    scores = [w["score"] for w in winners]
    prices = [w["price"] for w in winners]

    fig, ax1 = plt.subplots(figsize=(9, 5), dpi=300)

    x = range(len(profiles))
    width = 0.35

    color_score = "#1E88E5"
    color_price = "#E53935"

    rects1 = ax1.bar([i - width/2 for i in x], scores, width, label="Total Ranking Score (0-100)", color=color_score, alpha=0.85)
    ax1.set_ylabel("Composite Score", color=color_score, fontweight="bold")
    ax1.set_ylim(0, 110)
    ax1.tick_params(axis='y', labelcolor=color_score)

    ax2 = ax1.twinx()
    rects2 = ax2.bar([i + width/2 for i in x], prices, width, label="Winning Ticket Price (EUR)", color=color_price, alpha=0.85)
    ax2.set_ylabel("Ticket Price (EUR)", color=color_price, fontweight="bold")
    ax2.set_ylim(0, 70)
    ax2.tick_params(axis='y', labelcolor=color_price)

    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{p}\n({c})" for p, c in zip(profiles, companies)], fontsize=9)
    plt.title("Winning Offer Comparison Across Traveller Profiles (Madrid -> Malaga)", fontsize=12, fontweight="bold", pad=15)

    # Annotate values on top of bars
    for rect in rects1:
        h = rect.get_height()
        ax1.annotate(f"{h:.1f}", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold", color=color_score)

    for rect in rects2:
        h = rect.get_height()
        ax2.annotate(f"€{h:.2f}", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold", color=color_price)

    fig.tight_layout()
    out_path = OUT_DIR / "profile_comparison_chart.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    create_architecture_diagram()
    create_profile_comparison_chart()
