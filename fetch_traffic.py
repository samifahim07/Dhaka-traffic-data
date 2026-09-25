import requests
import csv
import os
import time
from datetime import datetime

SOUTH, WEST, NORTH, EAST = 23.70, 90.33, 23.90, 90.50

def fetch_traffic_roads():
    query = f"""
    [out:json][timeout:90];
    way["highway"](
      {SOUTH},{WEST},{NORTH},{EAST}
    );
    out body;
    """

    for attempt in range(3):
        try:
            response = requests.post(
                "https://overpass-api.de/api/interpreter",
                data={"data": query},
                timeout=90
            )

            if response.status_code != 200:
                print(f"Bad status: {response.status_code}, retrying...")
                time.sleep(15)
                continue

            if not response.text.strip():
                print(f"Empty response, retrying... (attempt {attempt+1})")
                time.sleep(15)
                continue

            data = response.json()
            elements = data.get("elements", [])
            print(f"Got {len(elements)} elements from API")
            break

        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}")
            time.sleep(15)
    else:
        # Still create CSV with error row so file always exists
        elements = []
        data = {"elements": []}

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile("traffic_data.csv")

    with open("traffic_data.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp", "road_id", "road_name",
                "road_type", "max_speed", "lanes", "oneway"
            ])

        if elements:
            for way in elements:
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
        else:
            # Write empty row so file always gets created
            writer.writerow([timestamp, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"])

    print(f"[{timestamp}] Done — {len(elements)} roads saved")

fetch_traffic_roads()
