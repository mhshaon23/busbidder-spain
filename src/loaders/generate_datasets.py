import csv
import json
from pathlib import Path
from datetime import datetime, timedelta

def generate_datasets():
    base_dir = Path(__file__).resolve().parent.parent.parent
    dest_path = base_dir / "data" / "destinations.json"
    with open(dest_path, "r", encoding="utf-8") as f:
        destinations = json.load(f)

    # 5 companies
    companies = [
        {"name": "SolRuta", "code": "SR", "type": "low_cost"},
        {"name": "Camino Express", "code": "CE", "type": "express"},
        {"name": "CostaLink", "code": "CL", "type": "coastal"},
        {"name": "VerdeBus", "code": "VB", "type": "eco"},
        {"name": "NocheVia", "code": "NV", "type": "night"},
    ]

    dates = ["2026-07-12", "2026-07-13", "2026-07-14"]
    offers = []
    offer_counter = 1000

    for d in destinations:
        dest_name = d["name"]
        dist = d["distance_km"]
        is_coastal = d["is_coastal"]

        # Base driving duration in minutes (~75-80 km/h average)
        base_mins = int((dist / 78.0) * 60)

        for comp in companies:
            c_name = comp["name"]
            c_code = comp["code"]
            c_type = comp["type"]

            # Customize according to company archetype
            if c_type == "low_cost":
                # SolRuta: budget, daytime, sometimes 1 transfer, non-ref
                dep_times = ["07:45", "11:30", "15:15"]
                price_factor = 0.055
                dur_factor = 1.15
                changeable = False
                refundable = False
                luggage = 12
                rating = 3.9
                co2 = round((dist * 0.038), 1)
                transfers = 1 if dist > 450 else 0

            elif c_type == "express":
                # Camino Express: direct, fast, higher price, flexible
                dep_times = ["08:30", "14:00", "17:30"]
                price_factor = 0.095
                dur_factor = 0.95
                changeable = True
                refundable = True
                luggage = 20
                rating = 4.7
                co2 = round((dist * 0.032), 1)
                transfers = 0

            elif c_type == "coastal":
                # CostaLink: specializes in coastal, slightly cheaper to coast
                dep_times = ["09:15", "13:45", "16:30"]
                price_factor = 0.068 if is_coastal else 0.082
                dur_factor = 1.05
                changeable = True
                refundable = False
                luggage = 25
                rating = 4.3
                co2 = round((dist * 0.035), 1)
                transfers = 0 if is_coastal else (1 if dist > 400 else 0)

            elif c_type == "eco":
                # VerdeBus: lowest CO2, electric/biogas, high rating
                dep_times = ["10:00", "15:00"]
                price_factor = 0.075
                dur_factor = 1.02
                changeable = True
                refundable = True
                luggage = 18
                rating = 4.8
                co2 = round((dist * 0.014), 1)  # very low eco footprint
                transfers = 0

            elif c_type == "night":
                # NocheVia: overnight departures
                dep_times = ["22:30", "23:45"]
                price_factor = 0.065
                dur_factor = 1.10
                changeable = True
                refundable = False
                luggage = 20
                rating = 4.2
                co2 = round((dist * 0.030), 1)
                transfers = 0

            # Generate offer for chosen dates and schedule
            for i, dt_str in enumerate(dates):
                # Pick a departure time variant based on date
                dep_time_str = dep_times[i % len(dep_times)]
                duration = int(base_mins * dur_factor)
                price = round(max(14.0, dist * price_factor + (5.0 if transfers > 0 else 0.0)), 2)
                seats = 15 + ((offer_counter * 7) % 35)

                # Compute arrival time
                dep_dt = datetime.strptime(f"{dt_str} {dep_time_str}", "%Y-%m-%d %H:%M")
                arr_dt = dep_dt + timedelta(minutes=duration)
                arr_time_str = arr_dt.strftime("%H:%M")

                offer_counter += 1
                offer_id = f"OFF-{c_code}-{offer_counter}"

                offers.append({
                    "offer_id": offer_id,
                    "company": c_name,
                    "origin": "Madrid",
                    "destination": dest_name,
                    "travel_date": dt_str,
                    "departure_time": dep_time_str,
                    "arrival_time": arr_time_str,
                    "duration_minutes": duration,
                    "price": price,
                    "transfers": transfers,
                    "luggage_kg": luggage,
                    "is_changeable": changeable,
                    "is_refundable": refundable,
                    "available_seats": seats,
                    "customer_rating": rating,
                    "co2_kg_per_passenger": co2,
                })

    # Save to data/offers.csv
    csv_path = base_dir / "data" / "offers.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(offers[0].keys()))
        writer.writeheader()
        writer.writerows(offers)

    print(f"Successfully generated {len(offers)} offers in {csv_path}")

    # Generate corrupt offers sample for validation tests
    corrupt_offers = [
        {
            "offer_id": "OFF-SR-9991",
            "company": "SolRuta",
            "origin": "Madrid",
            "destination": "Barcelona",
            "travel_date": "2026-07-12",
            "departure_time": "08:00",
            "arrival_time": "14:00",
            "duration_minutes": 360,
            "price": -25.50,  # Negative price!
            "transfers": 0,
            "luggage_kg": 15,
            "is_changeable": True,
            "is_refundable": False,
            "available_seats": 20,
            "customer_rating": 4.1,
            "co2_kg_per_passenger": 15.0,
            "expected_error": "Negative price"
        },
        {
            "offer_id": "OFF-CE-9992",
            "company": "Camino Express",
            "origin": "Madrid",
            "destination": "Atlantis",  # Unknown destination!
            "travel_date": "2026-07-12",
            "departure_time": "09:00",
            "arrival_time": "13:00",
            "duration_minutes": 240,
            "price": 45.00,
            "transfers": 0,
            "luggage_kg": 20,
            "is_changeable": True,
            "is_refundable": True,
            "available_seats": 10,
            "customer_rating": 4.8,
            "co2_kg_per_passenger": 12.0,
            "expected_error": "Unknown destination"
        },
        {
            "offer_id": "INVALID-ID",  # Invalid ID format!
            "company": "CostaLink",
            "origin": "Madrid",
            "destination": "Valencia",
            "travel_date": "2026-07-12",
            "departure_time": "10:00",
            "arrival_time": "14:30",
            "duration_minutes": 270,
            "price": 30.00,
            "transfers": 0,
            "luggage_kg": 20,
            "is_changeable": True,
            "is_refundable": False,
            "available_seats": 15,
            "customer_rating": 4.0,
            "co2_kg_per_passenger": 14.0,
            "expected_error": "Regex ID mismatch"
        },
        {
            "offer_id": "OFF-VB-9994",
            "company": "VerdeBus",
            "origin": "Madrid",
            "destination": "Seville",
            "travel_date": "2026-07-12",
            "departure_time": "10:00",
            "arrival_time": "15:00",
            "duration_minutes": 300,
            "price": 35.00,
            "transfers": 0,
            "luggage_kg": 18,
            "is_changeable": True,
            "is_refundable": True,
            "available_seats": 25,
            "customer_rating": 7.5,  # Rating > 5.0!
            "co2_kg_per_passenger": 6.0,
            "expected_error": "Rating exceeds bounds"
        },
        {
            "offer_id": "OFF-NV-9995",
            "company": "NocheVia",
            "origin": "Madrid",
            "destination": "Malaga",
            "travel_date": "2026-07-12",
            "departure_time": "23:00",
            "arrival_time": "05:00",
            "duration_minutes": 120,  # Temporal discrepancy: 6h travel but duration claims 2h!
            "price": 32.00,
            "transfers": 0,
            "luggage_kg": 20,
            "is_changeable": True,
            "is_refundable": False,
            "available_seats": 30,
            "customer_rating": 4.2,
            "co2_kg_per_passenger": 15.0,
            "expected_error": "Temporal discrepancy"
        }
    ]

    corrupt_csv_path = base_dir / "data" / "corrupt_offers_sample.csv"
    with open(corrupt_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(corrupt_offers[0].keys()))
        writer.writeheader()
        writer.writerows(corrupt_offers)

    print(f"Successfully generated corrupt test sample in {corrupt_csv_path}")

if __name__ == "__main__":
    generate_datasets()
