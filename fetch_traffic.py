import requests
import csv
import os
import time
from datetime import datetime

SOUTH, WEST, NORTH, EAST = 23.70, 90.33, 23.90, 90.50

def fetch_traffic_roads():
    query = f"""
    [out:json][timeout:60];
    way["highway"]["name"](
      {SOUTH},{WEST},{NORTH},{EAST}
    );
    out body;
    """

    # Try up to 3 times if API fails
    for attempt in range(3):
        try:
            response = requests.post(
                "https://overpass-api.de/api/interpreter",
                data={"data": query},
                timeout=60
            )

            # Check if response is valid
            if response.status_code != 200:
                print(f"Bad status code: {response.status_code}, retrying...")
                time.sleep(10)
                continue

            if not response.text.strip():
                print(f"Empty response, retrying... (attempt {attempt+1})")
                time.sleep(10)
                continue

            data = response.json()
            break  # success

        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}")
            time.sleep(10)
    else:
        print("All attempts failed. Skipping this run.")
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile("traffic_data.csv")

    with open("traffic_data.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp", "road_id", "road_name",
                "road_type", "max_speed", "lanes", "oneway"
            ])

        for way in data.get("elements", []):
            tags = way.get("tags", {})
            writer.writerow([
                timestamp,
                way.get("id"),
                tags.get("name", "N/A"),
                tags.get("highway", "N/A"),
                tags.get("maxspeed", "N/A"),
                tags.get("lanes", "N/A"),
                tags.get("oneway", "no"),
            ])

    print(f"[{timestamp}] Saved {len(data.get('elements', []))} roads")

fetch_traffic_roads()
