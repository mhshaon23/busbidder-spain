# BusBidder Spain: Project Status

**Course:** ACIT4420 Problem-solving with scripting (2026), OsloMet
**Student:** Mehmood Hasan
**Last updated:** 30 October 2026

## Current state

| Area | Status |
| :--- | :--- |
| Application | Complete: `--demo`, `--interactive`, `--quarantine` |
| Tests | 38 passing (`python -m pytest -v`) |
| Evidence | `outputs/01`–`08`, regenerated from the current code |
| Report | `report/BusBidder_Spain_Final_Report.docx` (editable) and `.pdf`, built by `report/build_report.py` |
| README | Up to date (commands, requirements, inputs, outputs, tests) |

## Still to do before submission

These are highlighted in yellow in the Word report and must be written by the student:

1. Student number (title page and README).
2. GitHub repository link and final commit hash (title page).
3. Submission date (title page).
4. The final paragraph of Section 10 (AI declaration): which parts were designed, written or substantially changed by the student, which AI suggestions were rejected, and how the final version was verified.

After editing in Word: right-click the table of contents and choose Update Field, then File > Save As > PDF over `report/BusBidder_Spain_Final_Report.pdf`. If the report is edited in Word, `report/build_report.py` no longer matches it, so do not rebuild the report from the script afterwards.

## Changes made on 30 October 2026

**Code**
- Seat capacity is now consistent between sessions: confirmed bookings in `data/bookings.json` are re-applied to the offers at start-up (`BookingManager.apply_existing_bookings`).
- Interactive mode asks for the traveller's own hard constraints (price, transfers, duration, luggage, changeable, refundable) and preferred departure, and prints a hard/soft summary before ranking. The demo prints the same summary.
- New Balanced profile with the specification's example weights (40/25/15/20).
- Missing data files raise `DataFileMissingError`; `main.py` shows known errors as a short message instead of a traceback.
- The explanation now compares the winner with the runner-up, warns when the margin is below 2 points, explains ties, and no longer mentions departure time when it is not a criterion.
- `rich` tables use a minimum width of 130 columns so they are not cut off.
- `data/companies.json` policy texts corrected to match the offer data.
- Eight new tests (capacity after restart, missing field values, zero seats, interactive constraints, hard/soft summary, missing-file error).

**Report**
- Rewritten in full, in journal style with APA 7 references, from the actual program output. The previous version reported offers that do not exist in the data (for example OFF-SR-1045 at EUR 29.15).
- New evaluation findings: the specification example is decided by 0.03 points; raising the budget from EUR 50 to EUR 51 changes the winner (rank reversal); a 5-point weight shift reverses the result; NocheVia wins none of 75 searches.
- `report/generate_figures.py` now computes the profile chart from the ranking engine, so the figure cannot drift from the program.
