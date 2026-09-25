import requests
import csv
import os
import time
from datetime import datetime

API_KEY = "acr7QCdblurzBRWJ04ic3SILqbBPi5ej"  

# Top 5 busiest roads in Dhaka 
ROUTES = [
    {
        "name": "Uttora → FarmGate",
        "origin": "23.8759,90.3795",
        "destination": "23.7578,90.3877"
    },
    {
        "name": "Mirpur → Motijhil",
        "origin": "23.8223,90.3654",
        "destination": "23.7334,90.4220"
    },
    {
        "name": "Jatrabari → Gulistan",
        "origin": "23.7104,90.4280",
        "destination": "23.7234,90.4075"
    },
    {
        "name": "Dhanmondi → Shahbagh",
        "origin": "23.7461,90.3742",
        "destination": "23.7387,90.3950"
    },
    {
        "name": "Gazipur → Banani",
        "origin": "23.9999,90.4203",
        "destination": "23.7936,90.4066"
    },
]

def fetch_travel_time(route):
    url = "https://api.tomtom.com/routing/1/calculateRoute/{origin}:{destination}/json".format(
        origin=route["origin"],
        destination=route["destination"]
    )
    params = {
        "key": API_KEY,
        "traffic": "true",
        "travelMode": "car"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        summary = data["routes"][0]["summary"]
        travel_time_min = round(summary["travelTimeInSeconds"] / 60, 1)
        no_traffic_min = round(summary["noTrafficTravelTimeInSeconds"] / 60, 1)
        delay_min = round((summary["travelTimeInSeconds"] - summary["noTrafficTravelTimeInSeconds"]) / 60, 1)
        distance_km = round(summary["lengthInMeters"] / 1000, 2)

        return {
            "travel_time_min": travel_time_min,
            "no_traffic_min": no_traffic_min,
            "delay_min": delay_min,
            "distance_km": distance_km
        }

    except Exception as e:
        print(f"Error for {route['name']}: {e}")
        return None

def collect_all_routes():
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile("traffic_data.csv")

    with open("traffic_data.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp", "route",
                "distance_km", "normal_time_min",
                "current_time_min", "delay_min"
            ])

        for route in ROUTES:
            result = fetch_travel_time(route)
            if result:
                writer.writerow([
                    timestamp,
                    route["name"],
                    result["distance_km"],
                    result["no_traffic_min"],
                    result["travel_time_min"],
                    result["delay_min"]
                ])
                print(f"✅ {route['name']} — {result['travel_time_min']} min (delay: {result['delay_min']} min)")
            else:
                writer.writerow([timestamp, route["name"], "N/A", "N/A", "N/A", "N/A"])

    print(f"[{timestamp}] Every Routs collect successfully!")

collect_all_routes()
