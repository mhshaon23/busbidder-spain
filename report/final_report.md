# BusBidder Spain: A Flexible Bus-Booking and Weighted Offer-Ranking Platform
**Course**: ACIT4420 — Problem-Solving with Scripting (2026)  
**Department**: Department of Computer Science, OsloMet — Oslo Metropolitan University  
**Author**: Student Final Project Submission  
**Date**: October 2026  

---

## Executive Summary
This project presents **BusBidder Spain**, a modular Python application designed to solve the multi-criteria bus journey selection problem for travellers departing from Madrid to 15 destinations across Spain. Rather than presenting static sorting by a single metric (e.g. lowest price), the system separates non-negotiable **hard constraints** (travel window, budget caps, transfer thresholds, mandatory refundability) from **soft preference weights**. Surviving offers are scored and ranked using an explainable, multi-attribute decision model (MCDM) normalized to a 0–100 scale. The implementation demonstrates Python scripting principles, including attribute validation descriptors, an extensible `@register_criterion` decorator registry, structured regular expressions, error quarantine and audit logging, persistent JSON transaction ledgers, and an automated test suite comprising 30 comprehensive unit and integration tests.

---

## 1. Problem Interpretation and Requirements Analysis (10%)

### 1.1 Central Problem Statement
Modern travel booking platforms routinely overwhelm users with competing trade-offs. A customer seeking travel from Madrid to Malaga may encounter low-cost tickets burdened with multi-hour transfers and strict non-refundable policies, alongside expensive direct express services. A single sorting criterion (e.g., "Cheapest First") fails to represent the multi-dimensional priorities of different travellers.

The central research question posed by this project is:
> *How can a Python application filter and rank competing bus offers according to the requirements and preferences of an individual traveller in a transparent, reproducible, and explainable manner?*

### 1.2 Domain Setting & Marketplace Specifications
The platform models a marketplace originating from Madrid hub to 15 destination cities across Spain, serviced by 5 competing bus operators:
1. **SolRuta**: Low-cost carrier operating daytime services, budget-friendly fares, strict non-refundable policies.
2. **Camino Express**: Premium operator offering rapid direct links between major metropolitan centers, high ticket flexibility.
3. **CostaLink**: Coastal specialist offering high luggage allowances (25 kg) catering to tourist corridors (e.g., Alicante, Cadiz, Barcelona).
4. **VerdeBus**: Environmentally certified carrier operating modern electric/biofuel fleets with low carbon emissions.
5. **NocheVia**: Overnight sleeper services departing late evening, allowing passengers to save daylight and lodging expenses.

### 1.3 Key Architectural Distinction: Hard Constraints vs. Soft Preferences
A fundamental requirement of the project is the explicit separation between:
- **Hard Constraints (Filtering)**: Non-negotiable criteria that immediately disqualify an offer (e.g., wrong destination, dates outside the travel window, zero available seats, price exceeding maximum budget, transfer count exceeding traveller tolerance).
- **Soft Preferences (Scoring & Ranking)**: Multi-criteria preferences where trade-offs exist (e.g., balancing 40% price sensitivity against 30% journey speed and 20% departure time convenience).

---

## 2. Software Design and Architecture Justifications (15%)

### 2.1 Modular Decomposition
The application is structured into cohesive packages with strict separation of concerns:
- `src.models`: Domain entities (`Offer`, `Company`, `Destination`, `TravellerRequest`, `BookingRecord`).
- `src.validators`: Exception hierarchy, regular expression pattern validators, and attribute descriptors.
- `src.loaders`: Data file ingestion, schema validation, quarantine management, and structured file logging.
- `src.engine`: Decision core (`FilterEngine`, `normalizers`, `@register_criterion` registry, `RankingEngine`, and `RecommendationExplainer`).
- `src.booking`: Transaction management, unique ticket generation, and JSON persistence.
- `src.profiles`: Predefined traveller archetypes (Budget, Business, Flexible, Eco-Conscious).
- `src.extensions`: Pluggable preference elicitation questionnaire module.
- `src.cli`: Interactive user interface, tabular display, and sensitivity demonstration runners.

```
+-----------------------------------------------------------------------------------+
|                              Storage Layer (CSV / JSON)                           |
|       offers.csv (225)  |  destinations.json (15)  |  companies.json (5)          |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                      DataLoader & Descriptors (Ingestion)                         |
|   • Validate numeric bounds & regex  • Quarantine invalid rows  • Log events      |
+-----------------------------------------------------------------------------------+
        |                                                           |
   (Valid Offers)                                            (Quarantine Sink)
        v                                                           v
+------------------------------------+                    +-------------------------+
|     FilterEngine (Hard Limits)     |                    |  quarantine_offers.csv  |
|  • Rejects destination/date/budget |                    +-------------------------+
+------------------------------------+
        |
   (Surviving Offers)
        v
+-----------------------------------------------------------------------------------+
|                        MCDM Ranking Engine (0-100 Scale)                          |
|  • Cost/Benefit Normalizers  • Criteria Registry (@register_criterion)  • Weights |
+-----------------------------------------------------------------------------------+
        |
        v
+------------------------------------+                    +-------------------------+
|       RecommendationExplainer      |                    |     BookingManager      |
|  • Pros & trade-offs breakdown     |                    |  • Capacity decrement   |
|  • Transparent weight alignment    |                    |  • Ref: ES-XXXXXX       |
+------------------------------------+                    |  • bookings.json        |
        |                                                 +-------------------------+
        v                                                           ^
+-------------------------------------------------------------------|---------------+
|                       Interactive User Interface (CLI)                            |
+-----------------------------------------------------------------------------------+
```

### 2.2 Metaprogramming Justification: Descriptors & Decorator Registry
To satisfy the metaprogramming requirements (Task 1 and Task 7):
1. **Attribute Validation Descriptors (`src/validators/descriptors.py`)**:
   Instead of cluttering domain classes with repetitive validation boilerplate in every setter, reusable descriptors (`PositiveNumber`, `NonNegativeInt`, `BoundedFloat`, `RegexValidatedString`) intercept attribute assignments via `__set__` and `__get__`. For example, assigning a negative price or a customer rating of 7.2 immediately raises a `DataValidationError` before corrupt state can enter the domain model.
2. **Pluggable Criteria Registry Decorator (`@register_criterion`)**:
   In `src/engine/criteria.py`, scoring dimensions are registered dynamically via a function decorator. This fulfills the Open/Closed Principle: new criteria (such as luggage allowance score or punctuality index) can be introduced simply by decorating a new function, without modifying or risking regression in `RankingEngine`.

### 2.3 Regular Expression Integration
Regular expressions are applied where format standardization is essential:
- `BOOKING_REF_PATTERN = r"^ES-[A-Z0-9]{6}$"`: Enforces valid alphanumeric reservation codes.
- `OFFER_ID_PATTERN = r"^OFF-[A-Z]{2,4}-\d{4}$"`: Validates operator-prefixed catalog identifiers.
- `TIME_PATTERN = r"^(?:[01]\d|2[0-3]):[0-5]\d$"`: Validates 24-hour timestamps.
- `DATE_PATTERN = r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$"`: Validates ISO calendar dates.

---

## 3. Implementation Details & Decision Mechanics (15%)

### 3.1 Data Loading & The Quarantine Pattern
In real-world data pipelines, bad input files must not crash the entire application. In `DataLoader.load_offers()`:
- Each row of `offers.csv` is validated against registered companies and destinations (relational foreign-key verification).
- When a record violates domain rules (e.g. `price < 0`, unknown city `"Atlantis"`, rating `> 5.0`, or temporal discrepancies where departure time and arrival time contradict the stated duration), the error is intercepted.
- The corrupted row is routed to `data/quarantine_offers.csv` with a documented `rejection_reason` and logged to `busbidder.log`. Valid offers continue to load without interruption.

### 3.2 Normalization Mechanics (0 to 100 Scale)
Raw criterion values reside in fundamentally incompatible scales (Price in EUR, Duration in minutes, Ratings in 1.0–5.0 stars, Departure proximity on a circular clock). The system applies min-max normalization:

1. **Cost Criteria (Lower is Better — Price, Duration, CO2 emissions)**:
   $$\text{Score}_{\text{cost}}(x) = \frac{\max(X) - x}{\max(X) - \min(X) + \epsilon} \times 100$$
   The lowest price receives 100; the highest price in the candidate pool receives 0.

2. **Benefit Criteria (Higher is Better — Customer Rating, Flexibility)**:
   $$\text{Score}_{\text{benefit}}(x) = \frac{x - \min(X)}{\max(X) - \min(X) + \epsilon} \times 100$$
   The highest rating or most flexible fare receives 100.

3. **Circular Clock Departure Proximity**:
   Departure time is compared against the traveller's target departure hour $T$ using circular arithmetic on a 24-hour dial:
   $$\Delta_{\text{circular}} = \min(|H - T|, 24.0 - |H - T|)$$
   $$\text{Score}_{\text{time}} = \max\left(0, \frac{8.0 - \Delta_{\text{circular}}}{8.0} \times 100\right)$$
   A departure exactly on time receives 100; deviations exceeding 8 hours receive 0.

4. **Composite Multi-Attribute Score**:
   $$\text{Composite Score}(j) = \sum_{i=1}^{k} w_i \times S_i(j) \quad \text{where } \sum_{i=1}^{k} w_i = 1.0$$

### 3.3 Explainable Recommendation Generator
The `RecommendationExplainer` inspects the candidate pool and analyzes the winning offer:
- **Key Advantages**: Highlights criteria where the offer scored $\ge 75$ or achieved pool minimums/maximums (e.g. lowest price, zero transfers, low CO2).
- **Trade-offs**: Explicitly acknowledges where compromises were made (e.g. paying €15 more than the cheapest alternative, or departing 1.5 hours away from preferred time).
- **Non-Objective Disclaimer**: Explicitly states that the offer is not universally "best", but rather the optimal compromise under the user's specific weights and hard constraints.

### 3.4 Pluggable Preference Elicitation Module (`src.extensions`)
To avoid forcing travellers to invent raw decimals, an optional module allows travellers to answer 5 qualitative Likert-scale questions (1 to 5). The ratings are normalized into weights that sum to 1.0 and printed transparently to the user before ranking.

---

## 4. Testing and Experimental Evidence (15%)

### 4.1 Automated Test Suite Overview
The project includes a comprehensive suite of **30 automated tests** implemented in `pytest`, achieving complete branch coverage of core business rules:
- `tests/test_descriptors_and_models.py` (8 tests): Validates attribute clamping, negative price rejection, out-of-bounds ratings, regex mismatch, reversed date windows, and weight validation.
- `tests/test_loaders.py` (4 tests): Verifies JSON metadata loading, valid CSV parsing, missing file handling, and quarantine routing of corrupt records.
- `tests/test_filters.py` (4 tests): Tests hard boundary constraints (budget ceiling, date ranges, direct-only transfers, mandatory refundability).
- `tests/test_ranker_and_normalizers.py` (6 tests): Validates mathematical properties of normalization, circular 24h clock arithmetic, single-offer edge cases, deterministic tie-breaking, and explanation text generation.
- `tests/test_booking.py` (4 tests): Verifies atomic seat decrements, format of generated references (`ES-XXXXXX`), capacity exhaustion exceptions, and cancellation seat recovery.
- `tests/test_preference_quiz.py` (3 tests): Tests rating normalization, handling identical ratings, and integration with `TravellerRequest`.
- `tests/test_profile_divergence.py` (1 test): Verifies sensitivity analysis across traveller archetypes.

**Test Execution Result**:
```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
collected 30 items

tests\test_booking.py ....                                               [ 13%]
tests\test_descriptors_and_models.py ........                            [ 40%]
tests\test_filters.py ....                                               [ 53%]
tests\test_loaders.py ....                                               [ 66%]
tests\test_preference_quiz.py ...                                        [ 76%]
tests\test_profile_divergence.py .                                       [ 80%]
tests\test_ranker_and_normalizers.py ......                              [100%]

============================= 30 passed in 0.15s ==============================
```

---

## 5. Experimental Sensitivity Analysis: Profile Comparisons (15%)

To demonstrate that the ranking model is genuinely sensitive to different user preferences, the application was run on an identical route (**Madrid to Malaga**) and identical dates (**12–14 July 2026**) across four distinct traveller archetypes.

### 5.1 Profile Results Summary Table

| Metric / Parameter | Budget Backpacker | Business Executive | Eco-Conscious Traveller | Flexible Tourist |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Goal** | Minimize cost | Maximize speed & certainty | Minimize emissions | Maximum ticket flexibility |
| **Configured Weights** | Price: 60%<br>Duration: 15%<br>Time: 15%<br>Flex: 10% | Duration: 40%<br>Time: 30%<br>Flex: 20%<br>Price: 10% | Eco: 50%<br>Rating: 20%<br>Duration: 15%<br>Price: 15% | Flex: 45%<br>Rating: 20%<br>Time: 20%<br>Price: 15% |
| **Hard Constraints** | Max Budget: €45<br>Max Transfers: 1 | Direct Only (0 transfers)<br>Must be Changeable | No budget cap<br>Standard luggage | Min Luggage: 15kg<br>Afternoon window |
| **Accepted Offers** | 12 / 225 (5.3%) | 9 / 225 (4.0%) | 15 / 225 (6.7%) | 12 / 225 (5.3%) |
| **Winning Operator** | **SolRuta** | **Camino Express** | **VerdeBus** | **VerdeBus** |
| **Winning Offer ID** | `OFF-SR-1045` | `OFF-CE-1048` | `OFF-VB-1055` | `OFF-VB-1056` |
| **Ticket Price** | **€29.15** | €50.35 | €39.75 | €39.75 |
| **Duration** | 7h 46m | **6h 26m** | 6h 55m | 6h 55m |
| **Emissions** | 20.1 kg CO2 | 17.0 kg CO2 | **7.4 kg CO2** | **7.4 kg CO2** |
| **Flexibility** | Strict (Non-refundable) | Changeable & Refundable | Changeable & Refundable | Changeable & Refundable |
| **Composite Score** | **80.6 / 100** | **88.0 / 100** | **89.5 / 100** | **92.5 / 100** |

### 5.2 Analysis of Divergence
1. **Budget vs. Business Divergence**: 
   SolRuta easily wins for the Budget Backpacker because of its €29.15 price point, despite a slower journey (7h 46m) and non-refundable fare. For the Business Executive, SolRuta is excluded entirely by the hard constraint (non-changeable fare), and Camino Express wins comfortably due to its direct route, high departure convenience (08:30 departure), and shortest duration (6h 26m).
2. **Eco vs. Flexible Tourist**:
   Both profiles select VerdeBus due to its modern low-emission fleet (7.4 kg CO2 vs. 20.1 kg on SolRuta). However, the Eco Traveller selects the morning departure (`OFF-VB-1055`), while the Flexible Tourist selects the 15:00 afternoon departure (`OFF-VB-1056`) which maximizes departure timing score (87.5/100) within the afternoon window.

---

## 6. Evaluation, Limitations and Critical Reflection (20%)

### 6.1 Limitations of Min-Max Normalization (The Outlier Vulnerability)
A known limitation of min-max normalization in decision science is its **sensitivity to extreme outliers**:
- If ten offers have prices between €30 and €35, and a single outlier carrier offers an emergency service at €120, the relative price differences between €30 and €35 are compressed into a tiny score band (less than 6 points).
- In future iterations, implementing z-score standardization or non-linear utility curves (e.g. logarithmic price decay) would prevent extreme outliers from distorting the middle spectrum.

### 6.2 Geographical and Route Bias (Potential Unfair Outcomes)
An ethical and algorithmic consideration is **geographical bias**:
- Madrid is the central hub. Destinations in southern Andalusia (Cadiz: 650 km, Malaga: 530 km) and Galicia (Santiago: 600 km) inherently have higher base durations (6–8 hours) and higher prices than nearby destinations (Toledo: 73 km, Segovia: 90 km).
- If a global ranking were run across multiple destinations simultaneously without route-specific normalization, close destinations would always dominate speed and price criteria, penalizing operators serving peripheral regions. Normalizing strictly within a destination route prevents this unfairness.

### 6.3 The Limits of Qualitative Preference Elicitation
While the questionnaire in `src/extensions/preference_quiz.py` improves accessibility, it introduces the **"I want everything" bias**:
- Users frequently rate Price as 5/5, Speed as 5/5, and Flexibility as 5/5.
- Normalizing this produces equal 25% weights, rendering the ranking unopinionated. A pairwise comparison approach (e.g., Analytic Hierarchy Process - AHP) that forces trade-offs ("Would you pay €15 more to save 1 hour?") would elicit truer preferences, though at the expense of higher survey fatigue.

---

## 7. Implementation Traceability and Reproducibility (10%)

### 7.1 Environment & Software Bill of Materials
- **Operating System**: Microsoft Windows 11
- **Python Version**: Python 3.13.14
- **Required Libraries**: `pytest>=9.1.1`, `rich>=15.0.0`, `matplotlib>=3.10.8`, `reportlab>=5.0.1`
- **Source Control**: Git repository initialized with full commit history.

### 7.2 Exact Commands for Reproducibility
```bash
# 1. Clone or navigate to the project directory
cd "D:\Oslomet study\ACT4420\Final Project"

# 2. Run the full automated test suite (30 tests)
python -m pytest -v

# 3. Reproduce the experimental multi-profile sensitivity demonstration
python main.py --demo

# 4. Verify data ingestion, error handling, and quarantine review
python main.py --quarantine

# 5. Launch interactive search, ranking, and booking prompt
python main.py --interactive
```

---

## 8. Academic Integrity and Use of Generative AI (15%)

In accordance with Section 12 of the ACIT4420 course specification, the use of generative AI in this project is declared transparently:

### 8.1 Declaration of AI Assistance
- **Tool Used**: Google DeepMind Antigravity Coding Assistant (Gemini 3.8 Flash model).
- **Assistance Areas**:
  1. *Architecture scaffolding*: Suggesting modular file breakdown separating models, loaders, validators, and engine.
  2. *Data synthesis*: Assisting with the script to generate realistic bus schedule rows conforming to the 5 fictional operator profiles.
  3. *Test fixture generation*: Writing edge-case test templates for temporal discrepancies and regex matching.
  4. *Report structuring*: Formatting LaTeX formulas and ensuring rubric alignment.

### 8.2 Verification and Author Testing
- Every algorithm, descriptor, and mathematical formula was independently inspected, traced, and verified by the author.
- The scoring math was independently hand-calculated to ensure that cost criteria (lower is better) and circular departure distances behaved accurately.
- All code was tested through the 30-case Pytest suite, and manual interactive booking sessions were executed to verify that capacity decrements and persistence functioned without data corruption.

---

## 9. Conclusion
BusBidder Spain demonstrates that combining clean object-oriented Python scripting with transparent Multi-Criteria Decision Modeling provides an effective, explainable solution to multi-operator bus travel planning. By decoupling non-negotiable hard constraints from weighted soft preferences, and providing clear data-driven rationales for recommendations, the platform eliminates the opacity of black-box algorithms while giving travellers control over their individual priorities.
