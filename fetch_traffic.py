import requests
import csv
import os
from datetime import datetime

# Dhaka city bounding box
SOUTH, WEST, NORTH, EAST = 23.70, 90.33, 23.90, 90.50

def fetch_traffic_roads():
    query = f"""
    [out:json][timeout:60];
    way["highway"]["name"](
      {SOUTH},{WEST},{NORTH},{EAST}
    );
    out body;
    """

    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query},
        timeout=60
    )

    data = response.json()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile("traffic_data.csv")

    with open("traffic_data.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header only once
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
