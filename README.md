# BusBidder Spain

**A Flexible Bus-Booking and Weighted Offer-Ranking Platform**  
*Department of Computer Science, OsloMet — ACIT4420 Problem-Solving with Scripting (2026)*

---

## 1. Project Overview

**BusBidder Spain** is a modular Python application that simulates a competitive transportation marketplace. Departing from **Madrid**, the platform aggregates, filters, and ranks bus journeys across **15 Spanish destinations** served by **5 distinct operators**:
1. **SolRuta**: Low-cost daytime services with frequent schedules.
2. **Camino Express**: Premium, direct connections between major metropolitan centers.
3. **CostaLink**: Coastal corridor specialists with generous luggage allowances.
4. **VerdeBus**: Environmentally certified operators featuring low-emission fleets.
5. **NocheVia**: Overnight sleeper services maximizing daytime utility.

The core algorithmic pipeline separates **non-negotiable hard constraints** (budget caps, date windows, transfer limits, mandatory refundability) from **soft preference ranking** using a transparent, multi-criteria decision model (MCDM) normalized to a 0–100 scale.

---

## 2. Technical Specifications

- **Python Version**: Python 3.10+ (tested on Python 3.13.14)
- **Primary Dependencies**:
  - `rich` (formatted terminal tables, panels, and styled output)
  - `pytest` (automated testing framework)
- **Standard Library Modules**: `csv`, `json`, `re`, `datetime`, `dataclasses`, `logging`, `pathlib`, `argparse`

---

## 3. Installation & Setup

1. **Clone or Extract the Repository**:
   ```bash
   cd "D:\Oslomet study\ACT4420\Final Project"
   ```

2. **Install Dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```

---

## 4. Program Entry Points & Execution Commands

### A. Run Automated Sensitivity Demonstration (Report Findings)
Compares 4 distinct traveller profiles (Budget, Business, Eco, and Flexible Tourist) on identical dates and routes, outputting score breakdowns and natural language justifications:
```bash
python main.py --demo
```

### B. Run Interactive Booking & Search Prompt
Launches an interactive prompt where users can pick destinations, travel windows, budgets, inspect ranked offers, and simulate atomic bookings:
```bash
python main.py --interactive
```

### C. Run Data Quarantine & Ingestion Review
Inspects rejected corrupt records, structured error types, and logging audits:
```bash
python main.py --quarantine
```

### D. Run Automated Test Suite
Executes the comprehensive Pytest suite (normal, invalid, boundary, and profile divergence test cases):
```bash
python -m pytest -v
```

---

## 5. Input Files & Data Storage

| Location | Format | Description |
| :--- | :--- | :--- |
| `data/destinations.json` | JSON | Registry of 15 destinations (distance in km, region, coastal flag) |
| `data/companies.json` | JSON | Profiles, cancellation rules, and eco status of the 5 operators |
| `data/offers.csv` | CSV | Base schedule catalogue (225+ offer records) |
| `data/corrupt_offers_sample.csv` | CSV | Controlled invalid test dataset (negative prices, invalid IDs, bad times) |
| `data/quarantine_offers.csv` | CSV | Quarantined records rejected during ingestion with logged failure causes |
| `data/bookings.json` | JSON | Persistent store of simulated bookings, tickets, and fare conditions |
| `busbidder.log` | Log File | Timestamped audit log of data loading, validations, and bookings |

---

## 6. Architecture & Advanced Techniques

- **Metaprogramming & Descriptors**: `src/validators/descriptors.py` implements custom descriptors (`PositiveNumber`, `NonNegativeInt`, `BoundedFloat`, `RegexValidatedString`) providing clean, declarative validation directly on entity attributes.
- **Pluggable Criteria Registry**: `src/engine/criteria.py` employs the `@register_criterion` decorator pattern, enabling modular addition of new scoring dimensions without modifying ranker core logic.
- **Regex Validation**: Purposeful validation of structured booking identifiers (`^ES-[A-Z0-9]{6}$`), offer codes (`^OFF-[A-Z]{2,4}-\d{4}$`), 24h timestamps, and ISO dates.
- **Explainability**: `RecommendationExplainer` contrasts the #1 ranked offer with alternatives, stating explicit advantages, acknowledged trade-offs, and avoiding misleading claims of objective superiority.

---

## 7. Automated Testing Summary

- **27 Automated Tests** in `tests/`:
  - `test_descriptors_and_models.py`: Attribute bounds, negative values, regex patterns, temporal consistency.
  - `test_loaders.py`: Ingestion, foreign key checks, quarantine handling, missing file resilience.
  - `test_filters.py`: Budget caps, travel dates, seat counts, transfers, flexibility requirements.
  - `test_ranker_and_normalizers.py`: Cost/benefit normalization math, circular clock distance, tie-breakers.
  - `test_booking.py`: Capacity decrements, regex ticket generation, seat exhaustion, cancellations.
  - `test_profile_divergence.py`: Demonstrates that Budget, Business, and Eco profiles produce distinct winners on identical search inputs.
