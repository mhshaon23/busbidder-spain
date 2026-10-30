# BusBidder Spain

**A bus-booking and weighted offer-ranking platform**
ACIT4420 Problem-solving with scripting (2026), final project, OsloMet

- **Student:** Mehmood Hasan
- **Student number:** _add your student number_
- **Report:** [`report/BusBidder_Spain_Final_Report.pdf`](report/BusBidder_Spain_Final_Report.pdf) (editable version: `report/BusBidder_Spain_Final_Report.docx`)

---

## 1. What the application does

BusBidder Spain is a command-line Python application for a fictional bus marketplace. Five companies (SolRuta, Camino Express, CostaLink, VerdeBus and NocheVia) offer journeys from Madrid to fifteen destinations. A traveller describes a request, and the application:

1. loads and validates the companies, destinations and 225 offers from files, and places invalid rows aside in a quarantine file;
2. removes the offers that break the traveller's **hard constraints** (destination, travel window, free seats, and optionally maximum price, maximum transfers, maximum duration, minimum luggage, changeable or refundable ticket);
3. ranks the remaining offers with a **weighted score** of criteria normalised to 0–100 (price, duration, departure-time convenience, flexibility, customer rating, emissions);
4. explains the top offer: its advantages, its remaining disadvantages, what separated it from the runner-up, and a warning when the result is a close call;
5. lets the traveller book an offer: it checks the seats, generates a booking reference (`ES-XXXXXX`), stores the fare conditions and saves the booking.

Before every ranking the application prints which conditions are hard constraints and which are soft preferences.

## 2. Requirements

- **Python:** 3.10 or newer (developed and tested with Python 3.13 on Windows 11)
- **Libraries** (see `requirements.txt`):
  - `rich`: formatted tables (optional; the program falls back to plain text tables)
  - `pytest`: automated tests
  - `matplotlib` and `python-docx`: only needed to rebuild the report figures and the Word report

Install them from the project folder:

```bash
python -m pip install -r requirements.txt
```

On systems where Python 3 is called `python3`, use `python3` instead of `python` in all commands.

## 3. Running the program

The entry point is **`main.py`** in the project folder. Run all commands from that folder.

| Command | What it does |
| :--- | :--- |
| `python main.py --demo` | Compares four traveller profiles on Madrid–Malaga, 12–14 July 2026 (also the default with no option) |
| `python main.py --interactive` | Interactive search: destination, dates, hard constraints, preferred departure, profile or questionnaire, ranking, explanation and booking |
| `python main.py --quarantine` | Shows rejected rows and the reason for each rejection |

```bash
python main.py --demo
```

```bash
python main.py --interactive
```

```bash
python main.py --quarantine
```

In interactive mode, pressing Enter accepts the default shown in brackets, and invalid input is rejected with a message and asked again. The traveller can either answer a five-question questionnaire (ratings 1–5 turned into weights) or choose one of five profiles: Budget Backpacker, Business Executive, Flexible Tourist, Eco-Conscious Traveller, or Balanced (the example weights from the specification). If a profile has its own hard constraints, the stricter of the profile's and the traveller's limits is used.

To reproduce the specification's example request (Madrid to Malaga, 12–14 July, max EUR 50, morning, max 1 transfer, changeable ticket), choose Malaga, keep the default dates, enter `50` as maximum price and `1` as maximum transfers, answer `y` to "changeable", enter `Morning`, answer `n` to the questionnaire and choose profile `5`.

## 4. Running the tests

```bash
python -m pytest -v
```

The 38 tests in `tests/` cover normal cases, invalid data, missing data (missing file, empty fields) and boundary cases (equal values, departures around midnight, zero seats, seat exhaustion). Tests that book seats write to a temporary folder and never change `data/bookings.json`.

## 5. Input files and outputs

| Location | Description |
| :--- | :--- |
| `data/companies.json` | The five companies, their profiles and cancellation policies |
| `data/destinations.json` | The fifteen destinations with distance from Madrid, region and coastal flag |
| `data/offers.csv` | 225 offers: 5 companies × 15 destinations × 3 days (12–14 July 2026) |
| `data/corrupt_offers_sample.csv` | Five deliberately invalid rows used to demonstrate validation |
| `data/quarantine_offers.csv` | Rows rejected during loading, with line number and reason (written by the program) |
| `data/bookings.json` | Booking ledger (written by the program) |
| `busbidder.log` | Timestamped log of loading, filtering, ranking and booking (written by the program) |
| `outputs/` | Saved program output used as evidence in the report (see below) |

**Seat capacity.** `offers.csv` is the original catalogue and is never rewritten. Each time the program starts, the seats in all confirmed bookings in `data/bookings.json` are subtracted from the loaded offers, so capacity stays consistent between sessions. Cancelled bookings are not subtracted. To reset all bookings, replace the content of `data/bookings.json` with `[]`.

**Evidence for the report** (`outputs/`):

| File | Content |
| :--- | :--- |
| `01_demo_four_profiles.txt` | Output of `--demo` |
| `02_specification_example_request.txt` | The specification's example request in interactive mode |
| `03_interactive_booking.txt` | A search and a booking of two seats, with the ticket |
| `04_capacity_after_restart.txt` | Seat capacity of the booked offer after a restart |
| `05_quarantine_review.txt` | Output of `--quarantine` |
| `06_test_results.txt` | Output of `python -m pytest -v` |
| `07_missing_file_error.txt` | Behaviour when a data file is missing |
| `08_busbidder_log_excerpt.log` | Log entries written while the evidence was produced |

## 6. Project structure

```
main.py                  entry point and interactive dialogue
src/models/              Offer, Company, Destination, TravellerRequest, BookingRecord
src/validators/          exception hierarchy, regular expressions, validation descriptors
src/loaders/             DataLoader (files, validation, quarantine), logger, dataset generator
src/engine/              FilterEngine, normalisers, criteria registry, RankingEngine, explainer
src/booking/             BookingManager (references, capacity, booking ledger)
src/profiles/            five traveller profiles
src/extensions/          preference questionnaire
src/cli/                 terminal tables, hard/soft summary, demonstration
tests/                   pytest test suite
data/                    input data and files written by the program
outputs/                 saved evidence used in the report
report/                  report (.docx, .pdf, .md), figures and build scripts
```

Design choices (descriptors, the `@register_criterion` registry, composition and inheritance, normalisation, ties and limitations) are explained in the report.

## 7. Rebuilding the report

The report text is defined in `report/build_report.py`.

```bash
python report/generate_figures.py
```

```bash
python report/build_report.py
```

```bash
python report/generate_pdf.py
```

`generate_pdf.py` uses Microsoft Word (Windows) to export the PDF. Without it, open the `.docx` in Word, update the table of contents and use File > Save As > PDF.

## 8. Known limitations

The data is simulated. Scores are relative to the offers in each search (min–max normalisation), so small price differences can be amplified and adding an offer can change the order of the others. NocheVia's overnight services never win under the current criteria. Bookings are stored in one JSON file and are not safe for simultaneous users. These points are discussed in Section 8 of the report.

## 9. Use of generative AI

Generative AI tools were used in this project. The tools, what they were used for and how the output was checked are declared in Section 10 of the report.
