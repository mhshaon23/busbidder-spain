# BusBidder Spain — Project Status & AI Handover Document

**Course**: OsloMet ACIT4420 — *Problem-Solving with Scripting (2026)*  
**Project**: BusBidder Spain — Final Project  
**Status**: Core Implementation & Test Suite 100% Complete; Ready for Academic Report Writing  
**Last Updated**: October 11, 2026  

---

## 1. Quick Start for Continuing AI / Developer

If you are an AI or human developer taking over this project, everything is fully modular, functional, and covered by automated tests.

### To verify the installation immediately:
```bash
# 1. Run all 27 unit and integration tests
python -m pytest -v

# 2. Run the multi-profile demonstration (Budget vs Business vs Eco vs Flexible Tourist)
python main.py --demo

# 3. Test interactive search, ranking, and booking
python main.py --interactive

# 4. Check data validation and quarantine handling
python main.py --quarantine
```

---

## 2. Completed Architecture & File Index

```
"d:\Oslomet study\ACT4420\Final Project"
│
├── data/
│   ├── companies.json              # 5 bus company profiles (SolRuta, Camino Express, CostaLink, VerdeBus, NocheVia)
│   ├── destinations.json           # 15 destination metadata records from Madrid hub
│   ├── offers.csv                  # 225 scheduled offers with multi-dimensional attributes
│   ├── corrupt_offers_sample.csv   # Controlled malformed test dataset for quarantine demonstration
│   ├── quarantine_offers.csv       # Ingestion quarantine sink capturing rejected records with logged reasons
│   └── bookings.json               # Persistent simulated booking ledger (tickets, references, capacity state)
│
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── destination.py          # Destination dataclass (distance, coastal flag, region)
│   │   ├── company.py              # Company dataclass (profile, cancellation rules, eco certification)
│   │   ├── offer.py                # Offer domain entity with descriptors & temporal consistency logic
│   │   ├── request.py              # TravellerRequest (hard constraints vs soft preferences)
│   │   └── booking.py              # BookingRecord entity with regex descriptor & ticket generator
│   │
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── exceptions.py           # Custom exception hierarchy (DataValidationError, BookingError, etc.)
│   │   ├── regex_patterns.py       # Regex patterns for Booking Refs, Offer IDs, 24h Times, ISO Dates
│   │   └── descriptors.py          # Metaprogramming descriptors (PositiveNumber, NonNegativeInt, BoundedFloat, RegexValidatedString)
│   │
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── data_loader.py          # Ingestion engine with type conversion, relational validation & quarantine
│   │   ├── generate_datasets.py    # Deterministic dataset synthesis script
│   │   └── logger.py               # Centralized logging configuration to busbidder.log and console
│   │
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── filters.py              # Hard constraint filter engine with survival rate audit statistics
│   │   ├── normalizers.py          # Min-max cost/benefit normalizations (0-100 scale) and circular clock delta
│   │   ├── criteria.py             # Metaprogramming: pluggable criteria registry via @register_criterion decorator
│   │   ├── ranker.py               # Weighted composite scoring engine with deterministic tie-breaking
│   │   └── explainer.py            # Natural language explanation generator (pros, trade-offs, weight alignment)
│   │
│   ├── profiles/
│   │   ├── __init__.py
│   │   └── archetypes.py           # 4 standard personas: Budget Backpacker, Business Executive, Flexible Tourist, Eco-Conscious
│   │
│   ├── booking/
│   │   ├── __init__.py
│   │   └── manager.py              # Transaction manager (atomic seat decrements, reference generator, JSON persistence)
│   │
│   └── cli/
│       ├── __init__.py
│       └── interface.py            # Rich terminal tables, colorized panels, and sensitivity demo runner
│
├── tests/
│   ├── test_descriptors_and_models.py   # Descriptors, bounds, negative values, temporal checks (8 tests)
│   ├── test_loaders.py                  # Ingestion, quarantine, missing files (4 tests)
│   ├── test_filters.py                  # Hard constraints: budget, seats, dates, transfers, flexibility (4 tests)
│   ├── test_ranker_and_normalizers.py   # Normalization math, criteria registry, explainability (6 tests)
│   ├── test_booking.py                  # Seat decrements, ticket generation, exhaustion, cancellations (4 tests)
│   └── test_profile_divergence.py       # Proves different profiles produce distinct winners on identical inputs (1 test)
│
├── main.py                         # Application CLI entry point
├── requirements.txt                # Dependencies (pytest, rich)
├── README.md                       # Comprehensive operational guide
├── busbidder.log                   # Audit log generated during executions
└── PROJECT_STATUS.md               # [THIS FILE] Handover and state tracking
```

---

## 3. Rubric & Requirement Compliance Matrix

| Requirement from Specification | Implementation Detail | Location |
| :--- | :--- | :--- |
| **Modular OOP Python App** | 7 cohesive packages separating models, validators, loaders, engine, booking, profiles, cli. | `src/` |
| **5 Companies & 15 Destinations** | Complete dataset with 225 offer permutations departing Madrid hub. | `data/companies.json`, `destinations.json`, `offers.csv` |
| **Metaprogramming / Techniques** | 1) Custom Python descriptors (`PositiveNumber`, `BoundedFloat`, etc.) for attribute validation.<br>2) Dynamic `@register_criterion` decorator registry pattern. | `src/validators/descriptors.py`, `src/engine/criteria.py` |
| **Data Validation & Quarantine** | Row-by-row validation; corrupt rows are quarantined into `quarantine_offers.csv` and logged. | `src/loaders/data_loader.py` |
| **Structured Regular Expressions** | Validation of booking references (`^ES-[A-Z0-9]{6}$`), Offer IDs, timestamps, and ISO dates. | `src/validators/regex_patterns.py` |
| **Custom Exception Hierarchy** | `BusBidderError` base with categorized subclasses for validation, constraints, and bookings. | `src/validators/exceptions.py` |
| **Hard vs Soft Distinction** | Hard constraints remove unacceptable offers in `FilterEngine`; soft preferences scored in `RankingEngine`. | `src/engine/filters.py`, `src/engine/ranker.py` |
| **Weighted Scoring Model** | Minimum 4 criteria (price, duration, departure time, flexibility) + rating and eco emissions. Scale 0–100. | `src/engine/normalizers.py`, `src/engine/criteria.py` |
| **Explainable Recommendation** | Natural language rationale highlighting advantages, trade-offs, and weight impact (no false objective claim). | `src/engine/explainer.py` |
| **Simulated Booking Management** | Capacity decrement, unique reference generation, persistent store, and ticket printing. | `src/booking/manager.py` |
| **3+ Traveller Profiles** | Budget Backpacker, Business Executive, Flexible Tourist, Eco-Conscious Traveller. | `src/profiles/archetypes.py` |
| **Automated Tests** | 27 passing tests covering normal, invalid, edge, missing data, and profile divergence. | `tests/` |

---

## 4. Next Steps for Next Developer / AI

The implementation is functionally complete and tested. The remaining deliverable according to Section 9 of the specification is the **Final Report (PDF format)**.

### Priority Next Steps:
1. **Prepare Report Draft (`report/report_draft.md`)**:
   - Section 1: Problem Interpretation and Requirements Analysis (10%)
   - Section 2: Software Design & Architecture Justifications (15%)
     - Justify composition vs inheritance.
     - Justify descriptors (metaprogramming) and `@register_criterion` registry decorator.
     - Include Mermaid architecture and flow diagrams.
   - Section 3: Implementation Explanation (15%)
     - Hard constraint filtering vs soft preference normalization.
     - Mathematical scoring equations.
   - Section 4: Testing & Experimental Evidence (15%)
     - Document the 27 Pytest cases, quarantine log extracts, and terminal screenshots/tables.
   - Section 5: Evaluation, Limitations and Critical Reflection (20%)
     - Discuss potential unfair outcomes (e.g., bias against remote destinations, time sensitivity vs price).
     - Trade-offs in normalization methods (min-max sensitivity to outliers).
   - Section 6: Traceability & Reproducibility (10%)
     - Exact commands, commit history, file manifest.
   - Section 7: Academic Integrity & Generative-AI Declaration (15%)
     - Transparent declaration of how generative AI was used, verified, and tested.

2. **Generate Visual Diagrams & Tables**:
   - Use `python main.py --demo > demo_output.txt` to capture experimental runs for inclusion in the report.
