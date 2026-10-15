# BusBidder Spain — Project Status & AI Handover Document

**Course**: OsloMet ACIT4420 — *Problem-Solving with Scripting (2026)*  
**Project**: BusBidder Spain — Final Project  
**Current State**: 100% Complete. Contains all code, tests (30/30), data files, documentation, and the complete academic final report in both Markdown (`report/final_report.md`) and compiled PDF (`report/BusBidder_Spain_Final_Report.pdf`).  
**Last Updated**: October 15, 2026  

---

## 1. Quick Start for Another AI (How to Use This Document)

> **IMPORTANT FOR ANY AI WRITING OR EDITING THE REPORT**:  
> You **do not need to read the entire codebase** from scratch. Everything you need to know about the system architecture, mathematical formulas, experimental evidence, robustness features (like input re-prompting), and ethical reflections is documented in full detail in this file and in [`report/final_report.md`](file:///d:/Oslomet%20study/ACT4420/Final%20Project/report/final_report.md).

### Quick Verification Commands:
```bash
# 1. Run all 30 unit and integration tests (takes ~0.15s)
python -m pytest -v

# 2. Run the 4-profile sensitivity demonstration (Budget vs Business vs Eco vs Flexible)
python main.py --demo

# 3. Run interactive trip search, ranking, and ticket booking
python main.py --interactive

# 4. Check data validation and quarantine handling
python main.py --quarantine

# 5. Re-compile the PDF report if needed
python report/generate_pdf.py
```

---

## 2. Directory Structure & File Index

```
"d:\Oslomet study\ACT4420\Final Project"
│
├── data/
│   ├── companies.json              # 5 bus company profiles (SolRuta, Camino Express, CostaLink, VerdeBus, NocheVia)
│   ├── destinations.json           # 15 destination records from Madrid hub
│   ├── offers.csv                  # 225 scheduled bus offers across 15 cities and 5 companies
│   ├── corrupt_offers_sample.csv   # Deliberately malformed rows used for testing quarantine handling
│   ├── quarantine_offers.csv       # Sinks rows that fail validation during CSV loading
│   └── bookings.json               # JSON ledger where simulated bookings and tickets are persisted
│
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── destination.py          # Destination model (name, distance in km, region, is_coastal flag)
│   │   ├── company.py              # Company model (name, code, profile, cancellation policy, eco flag)
│   │   ├── offer.py                # Offer domain entity with descriptors & departure/arrival consistency checks
│   │   ├── request.py              # TravellerRequest (separates hard constraints from soft weights)
│   │   └── booking.py              # BookingRecord model with regex validation & text ticket printer
│   │
│   ├── validators/
│   │   ├── exceptions.py           # Custom exception hierarchy (DataValidationError, BookingError, etc.)
│   │   ├── regex_patterns.py       # Regex for Booking Ref (ES-XXXXXX), Offer ID, 24h Time, ISO Date
│   │   └── descriptors.py          # Metaprogramming: Custom descriptors for attribute validation
│   │
│   ├── loaders/
│   │   ├── data_loader.py          # Reads JSON/CSV, foreign key checks, quarantines bad rows
│   │   ├── generate_datasets.py    # Script that generated the 225 offers and test corrupt files
│   │   └── logger.py               # Writes logs to busbidder.log and warnings to console
│   │
│   ├── engine/
│   │   ├── filters.py              # Hard constraint filter engine with rejection statistics
│   │   ├── normalizers.py          # Min-max 0-100 normalization (cost, benefit, 24h circular clock)
│   │   ├── criteria.py             # Metaprogramming: @register_criterion decorator & registry pattern
│   │   ├── ranker.py               # Weighted composite scoring engine and deterministic tie-breaking
│   │   └── explainer.py            # Generates transparent plain-English explanation for the top offer
│   │
│   ├── profiles/
│   │   └── archetypes.py           # 4 student-designed traveller profiles for testing
│   │
│   ├── extensions/
│   │   └── preference_quiz.py      # Pluggable module: prompts 1-5 quiz to calculate normalized weights
│   │
│   ├── booking/
│   │   └── manager.py              # Books tickets, decrements seats, creates ES-XXXXXX references
│   │
│   └── cli/
│       └── interface.py            # Display tables, fallback ASCII tables, and demonstration runner
│
├── tests/
│   ├── test_descriptors_and_models.py   # Tests descriptors, invalid prices, dates, regex (8 tests)
│   ├── test_loaders.py                  # Tests reading JSON/CSV, quarantine file, missing files (4 tests)
│   ├── test_filters.py                  # Tests hard filters (dates, budget, transfers, luggage) (4 tests)
│   ├── test_ranker_and_normalizers.py   # Tests 0-100 normalization, ranking math, explanations (6 tests)
│   ├── test_booking.py                  # Tests seat reduction, unique reference, cancellation (4 tests)
│   ├── test_preference_quiz.py          # Tests 1-5 rating normalization, edge cases, sum to 1.0 (3 tests)
│   └── test_profile_divergence.py       # Proves that different profiles pick different winners (1 test)
│
├── report/
│   ├── final_report.md                  # Comprehensive academic report in Markdown
│   ├── BusBidder_Spain_Final_Report.pdf # Publication-ready 4-page PDF final report
│   ├── architecture_diagram.png         # High-resolution component architecture diagram
│   ├── profile_comparison_chart.png     # Sensitivity comparison chart across traveller profiles
│   ├── generate_figures.py              # Matplotlib script that generates the figures
│   └── generate_pdf.py                  # ReportLab compilation script
│
├── main.py                         # CLI entry point (supports --demo, --interactive, --quarantine)
├── requirements.txt                # Dependencies (pytest, rich, matplotlib, reportlab)
├── README.md                       # Student project overview and setup instructions
├── busbidder.log                   # Application audit log file
└── PROJECT_STATUS.md               # [THIS FILE] Handover and tracking document
```

---

## 3. Comprehensive Feature & Robustness Summary (For Report Writing)

### A. Strict Input Validation & Error Re-Prompting (Interactive Robustness)
In `main.py` and `src/extensions/preference_quiz.py`, all user interactions are wrapped in **validation loops (`while True`)** with explicit, descriptive error messages that re-ask the exact same question rather than crashing:
1. **Destination Selection**: Accepts either a destination number (1–15) or city name (case-insensitive). If an invalid string like `"Narnia"` is typed, prints:
   `Error: Unknown destination 'Narnia'. Please enter a number (1-15) or a city name from the list above.` $\to$ Re-prompts.
2. **Date Inputs (`d_from` and `d_to`)**:
   - Validated against regex pattern `r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$"`.
   - Verified that `d_to >= d_from`. If an end date earlier than the start date is typed (e.g. `2026-07-10` after `2026-07-12`), prints:
     `Error: Travel end date (2026-07-10) cannot be earlier than start date (2026-07-12).` $\to$ Re-prompts.
3. **Customization Prompt (Preference Quiz)**:
   - Asks: `"Would you like to customize your search preferences? Answer 5 quick questions (y/n) [Default: n]: "`
   - Validates response is in `('y', 'yes', 'n', 'no', '')`. If invalid like `"maybe"`, prints:
     `Error: Invalid response 'maybe'. Please enter 'y' for yes or 'n' for no.` $\to$ Re-prompts.
   - **Bypass Logic**: If the user selects `y`, they answer the 5 questions, weights are calculated, and the **4 preset archetypes are completely bypassed!** Only if they select `n` are the 4 preset archetypes prompted.
4. **Archetype Selection (1–4)**:
   - Options are described in friendly plain language without raw percentages:
     - `[1] Budget Backpacker (Price is given more priority, accepts transfers to save money)`
     - `[2] Business Executive (Fastest direct travel and departure time are given priority)`
     - `[3] Flexible Tourist (Ticket changes, refunds, and luggage are given priority)`
     - `[4] Eco-Conscious Traveller (Lowest CO2 emissions and green transport are given priority)`
   - Rejects inputs outside 1–4 with clear error feedback and re-prompts.
5. **Booking Confirmation & Seat Selection**:
   - Rejects non-integers or seat numbers exceeding available bus capacity:
     `Error: Cannot book 50 seat(s). Only 15 seat(s) available on this bus.` $\to$ Re-prompts.

### B. Metaprogramming Implementations
1. **Custom Python Descriptors (`src/validators/descriptors.py`)**:
   - `ValidatedAttribute`: Base descriptor implementing `__set_name__`, `__get__`, `__set__`.
   - `PositiveNumber`: Enforces numeric $> 0$ (for ticket price, duration, CO2).
   - `NonNegativeInt`: Enforces integer $\ge 0$ (for seat inventory and transfer count).
   - `BoundedFloat`: Enforces range $[min, max]$ (for customer star rating 1.0 to 5.0).
   - `RegexValidatedString`: Enforces string regex patterns (for Offer IDs and Booking References).
2. **Pluggable Criteria Registry Decorator (`@register_criterion`)**:
   - In `src/engine/criteria.py`, scoring dimensions are registered dynamically via a decorator into `CRITERIA_REGISTRY`. This enables adding new criteria without touching the ranking engine.

### C. Normalization & Multi-Criteria Decision Math
Converts disparate physical units (Euros, minutes, star ratings, departure clock) to a standardized 0–100 scale:
- **Cost Criteria (Lower is Better — Price, Duration, CO2 emissions)**:
  $$\text{Score}_{\text{cost}}(x) = \frac{\max(X) - x}{\max(X) - \min(X)} \times 100$$
- **Benefit Criteria (Higher is Better — Customer Rating, Flexibility)**:
  $$\text{Score}_{\text{benefit}}(x) = \frac{x - \min(X)}{\max(X) - \min(X)} \times 100$$
- **Circular Clock Departure Proximity**:
  Calculates minimal angular distance on a 24-hour dial:
  $$\Delta_{\text{circular}} = \min(|H - T|, 24.0 - |H - T|)$$
  $$\text{Score}_{\text{time}} = \max\left(0, \frac{8.0 - \Delta_{\text{circular}}}{8.0} \times 100\right)$$
- **Total Composite Score**:
  $$\text{Total Score}(j) = \sum_{i=1}^{k} w_i \times S_i(j) \quad \text{where } \sum w_i = 1.0$$

### D. Experimental Findings: Profile Comparison on Madrid -> Malaga (12-14 July 2026)
This experimental dataset is pre-computed and proven in `main.py --demo` and `tests/test_profile_divergence.py`:

| Profile | Winning Operator & Offer ID | Ticket Price | Journey Duration | CO2 Emissions | Flexibility Policy | Total Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Budget Backpacker** | **SolRuta** (`OFF-SR-1045`) | **€29.15** | 7h 46m (1 transfer) | 20.1 kg | Strict (Non-refundable) | **80.6 / 100** |
| **Business Executive** | **Camino Express** (`OFF-CE-1048`) | €50.35 | **6h 26m** (Direct) | 17.0 kg | Changeable & Refundable | **88.0 / 100** |
| **Eco-Conscious Traveller** | **VerdeBus** (`OFF-VB-1055`) | €39.75 | 6h 55m (Direct) | **7.4 kg** | Changeable & Refundable | **89.5 / 100** |
| **Flexible Tourist** | **VerdeBus** (`OFF-VB-1056`) | €39.75 | 6h 55m (Direct) | **7.4 kg** | Changeable & Refundable | **92.5 / 100** |

### E. Explainability & Non-Objective Disclaimer
The system explicitly avoids claiming that the top offer is "objectively best". The `RecommendationExplainer` generates:
- **Key Advantages** (e.g. lowest price, direct route, low CO2).
- **Trade-offs** (e.g. costs €15 more than budget options, or departs 1 hour away from target time).
- **Mandatory Disclaimer**: *"This offer is not objectively superior in every aspect; it represents the best compromise under your specific constraints, scoring rules, and preference weights."*

### F. Critical Evaluation & Limitations (For Rubric Section 6)
1. **Min-Max Outlier Vulnerability**: An extreme high-price luxury outlier compresses the score differences between standard economy fares into a narrow band (< 5 points).
2. **Geographical Equity**: Long-haul peripheral destinations (Cadiz: 650 km, Santiago: 600 km) inherently have higher base durations and prices than close cities (Toledo: 73 km). Normalizing strictly within destination routes avoids geographic penalization.
3. **Preference Elicitation Survey Bias**: People tend to rate all factors 5/5 ("I want everything"), which normalizes to an unopinionated 20% equal weighting.

---

## 4. Submission Files & Ready Deliverables
1. **PDF Final Report**: [`report/BusBidder_Spain_Final_Report.pdf`](file:///d:/Oslomet%20study/ACT4420/Final%20Project/report/BusBidder_Spain_Final_Report.pdf) (4 pages with diagrams and tables).
2. **Markdown Final Report**: [`report/final_report.md`](file:///d:/Oslomet%20study/ACT4420/Final%20Project/report/final_report.md).
3. **Automated Test Suite**: 30 passing tests in `tests/`.
4. **Catalog Data**: 225 offers across 15 destinations and 5 companies in `data/`.
5. **Git Repository**: Initialized with clean descriptive commit history.
