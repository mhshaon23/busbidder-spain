# BusBidder Spain — Project Status & AI Handover Document

**Course**: OsloMet ACIT4420 — *Problem-Solving with Scripting (2026)*  
**Project**: BusBidder Spain — Final Project  
**Current State**: 100% Complete (Code, Tests 30/30, Data, Documentation, and Final Academic Report in PDF & Markdown).  
**Last Updated**: October 15, 2026  

---

## 1. Quick Start for the Next AI / Developer

Everything is functional, clean, and fully tested. All project deliverables required by the OsloMet ACIT4420 specification are complete and ready for submission:
1. **Source Code**: Modular Python code written in a clean, student-authentic style.
2. **Automated Tests**: 30 comprehensive unit and integration tests passing in 0.15s.
3. **Datasets & Quarantine**: JSON and CSV datasets with robust validation and error quarantine.
4. **Final Academic Report**: Completed in both Markdown (`report/final_report.md`) and compiled publication-quality PDF (`report/BusBidder_Spain_Final_Report.pdf`) featuring architecture diagrams and experimental comparison charts.

### Verification Commands:
```bash
# 1. Run all 30 unit and integration tests
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

## 2. Directory Structure & File Map

```
"d:\Oslomet study\ACT4420\Final Project"
│
├── data/
│   ├── companies.json              # 5 bus company profiles (SolRuta, Camino Express, CostaLink, VerdeBus, NocheVia)
│   ├── destinations.json           # 15 destination records from Madrid hub
│   ├── offers.csv                  # 225 scheduled bus offers
│   ├── corrupt_offers_sample.csv   # Deliberately malformed rows used for testing quarantine handling
│   ├── quarantine_offers.csv       # Sinks rows that fail validation during CSV loading
│   └── bookings.json               # JSON file where simulated bookings are saved
│
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── destination.py          # Destination model (name, distance, region, coast flag)
│   │   ├── company.py              # Company model (name, code, profile, cancellation policy)
│   │   ├── offer.py                # Offer model with descriptors & cross-time validation
│   │   ├── request.py              # TravellerRequest (separates hard constraints from soft weights)
│   │   └── booking.py              # BookingRecord model with regex validation & text ticket printer
│   │
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── exceptions.py           # Custom exception classes (DataValidationError, BookingError, etc.)
│   │   ├── regex_patterns.py       # Regex for Booking Ref (ES-XXXXXX), Offer ID, 24h Time, ISO Date
│   │   └── descriptors.py          # Custom descriptors for attribute validation (metaprogramming)
│   │
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── data_loader.py          # Loads JSON/CSV files, checks keys, quarantines bad rows
│   │   ├── generate_datasets.py    # Script that created the 225 offers and test corrupt files
│   │   └── logger.py               # Writes logs to busbidder.log
│   │
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── filters.py              # Hard constraint filter engine with rejection statistics
│   │   ├── normalizers.py          # Min-max 0-100 normalization (cost, benefit, 24h circular clock)
│   │   ├── criteria.py             # @register_criterion decorator & registry pattern
│   │   ├── ranker.py               # Weighted composite scoring engine and tie-breaking
│   │   └── explainer.py            # Generates plain-English explanation for the top offer
│   │
│   ├── profiles/
│   │   ├── __init__.py
│   │   └── archetypes.py           # 4 student-designed traveller profiles for testing
│   │
│   ├── extensions/
│   │   ├── __init__.py
│   │   └── preference_quiz.py      # Pluggable module: prompts 1-5 quiz to calculate normalized weights
│   │
│   ├── booking/
│   │   ├── __init__.py
│   │   └── manager.py              # Books tickets, decrements seats, creates ES-XXXXXX references
│   │
│   └── cli/
│       ├── __init__.py
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

## 3. Rubric Compliance Verification

| Rubric Component (Weight) | Status | Where to Inspect |
| :--- | :---: | :--- |
| **Problem Interpretation & Requirements (10%)** | Complete | Report Section 1 & `README.md` |
| **Software Design & Architecture Justifications (15%)** | Complete | Report Section 2, `src/validators/descriptors.py`, `src/engine/criteria.py`, and `Figure 1` |
| **Implementation Explanation (15%)** | Complete | Report Section 3, `src/loaders/data_loader.py`, `src/engine/filters.py`, `src/engine/normalizers.py` |
| **Testing & Experimental Evidence (15%)** | Complete | Report Section 4, `tests/` (30 passing tests in 0.15s) |
| **Evaluation, Limitations & Critical Reflection (20%)** | Complete | Report Section 6 (Outlier vulnerability, geographic equity, preference elicitation limits) |
| **Traceability & Reproducibility (10%)** | Complete | Report Section 7, Git commit log, exact terminal commands |
| **Academic Integrity & Generative-AI Use (15%)** | Complete | Report Section 8 (Detailed declaration of AI tool, areas of assistance, and verification steps) |

---

## 4. Deliverables Ready for Submission

The folder contains all required submission contents as defined in Section 11 of the specification:
1. `report/BusBidder_Spain_Final_Report.pdf` (Primary deliverable in PDF format).
2. Complete, tested Python source code across modular packages.
3. `README.md` with setup, dependency, and execution instructions.
4. Input datasets in `data/`.
5. Automated test suite with 30 tests.
6. `requirements.txt` with dependency specifications.
7. Clean Git repository commit history.
