"""
Sofia Water Scraper - Civic Tech App Backend
Scrapes public data about water disruptions from Sofiyska Voda ArcGIS API
Output: Updates disruptions.json with water repair details
"""

import os
import json
import time
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any
from pyproj import Transformer

# Determine the correct path for disruptions.json regardless of where the script is run
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == "scrapers":
    output_path = os.path.join(os.path.dirname(current_dir), "data", "disruptions.json")
else:
    output_path = os.path.join(current_dir, "backend", "data", "disruptions.json")

# Configuration
CONFIG = {
    "output_file": output_path,
    "request_timeout": 15,
}

ARCGIS_URL = (
    "https://gispx.sofiyskavoda.bg/arcgis/rest/services/"
    "WSI_PUBLIC/InfoCenter_Public/MapServer/2/query"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://gispx.sofiyskavoda.bg/WebApp.InfoCenter/?a=0&tab=0",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "*/*",
}

# Convert from UTM35N (EPSG:32635) -> WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:32635", "EPSG:4326", always_xy=True)

class WaterDisruptionScraper:
    def __init__(self):
        self.session = requests.Session()
        
    def polygon_centroid(self, rings: list) -> tuple[float, float]:
        """Calculates the center of a polygon (middle point of all vertices)."""
        all_x, all_y = [], []
        for ring in rings:
            for point in ring:
                all_x.append(point[0])
                all_y.append(point[1])
        if not all_x or not all_y:
            return 0.0, 0.0
        return sum(all_x) / len(all_x), sum(all_y) / len(all_y)

    def to_wgs84(self, x: float, y: float) -> tuple[float, float]:
        """Convert from EPSG:32635 to WGS84 (latitude, longitude)."""
        lon, lat = transformer.transform(x, y)
        return round(lat, 6), round(lon, 6)

    def ms_to_date(self, ms: int) -> str:
        """Convert timestamp in milliseconds to 'YYYY-MM-DD'."""
        if not ms:
            return ""
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")

    def make_id(self, alert_id: str, location: str) -> str:
        """Generate a unique ID."""
        slug = str(location).lower()[:20].replace(" ", "_").replace(".", "")
        ts = time.time()
        return f"water_{slug}_{alert_id}_{round(ts, 3)}"

    def fetch_water_stops(self) -> List[Dict[str, Any]]:
        """Fetches and parses the water stops from the ArcGIS API."""
        # Get session cookie first
        try:
            self.session.get(
                "https://gispx.sofiyskavoda.bg/WebApp.InfoCenter/?a=0&tab=0",
                headers=HEADERS,
                timeout=10,
            )
        except Exception as e:
            print(f" Failed to get session cookie: {e}")

        # Fetch the geometry data
        try:
            response = self.session.get(
                ARCGIS_URL,
                params={
                    "f": "json",
                    "where": "1=1",
                    "outFields": "*",
                    "returnGeometry": "true",
                    "d": int(time.time() * 1000),
                },
                headers=HEADERS,
                timeout=CONFIG["request_timeout"],
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f" Failed to fetch water disruptions: {e}")
            return []

        features = data.get("features", [])
        scraped_at = datetime.now(tz=timezone.utc).isoformat()
        results = []

        for feature in features:
            attrs = feature.get("attributes", {})
            geometry = feature.get("geometry", {})

            # Calculate coordinates
            lat, lon = None, None
            rings = geometry.get("rings")
            if rings:
                try:
                    cx, cy = self.polygon_centroid(rings)
                    lat, lon = self.to_wgs84(cx, cy)
                except Exception:
                    pass

            # Fallback to Sofia center if coordinates couldn't be parsed
            if not lat or not lon:
                lat, lon = 42.6977, 23.3219

            disruption_type = "Water repair"
            original_type = attrs.get("ALERTTYPE")
            if not original_type or str(original_type).strip().lower() in ("null", "none", ""):
                original_type = "Спиране на водата"

            results.append({
                "id": self.make_id(str(attrs.get("ALERTID", "")), attrs.get("LOCATION", "")),
                "street": attrs.get("LOCATION", "Unknown Location"),
                "disruption_type": disruption_type,
                "description": str(original_type),
                "start_date": self.ms_to_date(attrs.get("START_")),
                "end_date": self.ms_to_date(attrs.get("ALERTEND")),
                "latitude": lat,
                "longitude": lon,
                "scraped_at": scraped_at,
                "source": "water_supply"
            })

        return results

    def merge_and_save(self, new_data: List[Dict[str, Any]]) -> None:
        """Merges new water data into the existing disruptions.json file."""
        existing_data = {"timestamp": datetime.now().isoformat(), "count": 0, "disruptions": []}
        output_file = CONFIG["output_file"]
        
        try:
            if os.path.exists(output_file):
                with open(output_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
        except Exception as e:
            print(f" Could not load existing disruptions (will create new): {e}")

        all_disruptions = existing_data.get("disruptions", [])
        
        # Filter out all old water disruptions to prevent duplicates
        filtered_disruptions = []
        for d in all_disruptions:
            is_water = (
                d.get("source") == "water_supply" 
                or d.get("disruption_type") == "Water outage" 
                or str(d.get("id")).startswith("water_")
            )
            if not is_water:
                filtered_disruptions.append(d)

        # Append fresh water disruptions
        filtered_disruptions.extend(new_data)

        # Update metadata
        existing_data["disruptions"] = filtered_disruptions
        existing_data["count"] = len(filtered_disruptions)
        existing_data["timestamp"] = datetime.now().isoformat()

        # Save to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            print(f" Saved {len(new_data)} water disruptions.")
            print(f" Total disruptions now tracked: {len(filtered_disruptions)}")
            print(f" Data written to {output_file}")
        except Exception as e:
            print(f" Failed to save JSON: {str(e)}")

    def run(self) -> None:
        """Main execution flow for the scraper."""
        print(" Starting Water Disruptions Scraper...")
        water_disruptions = self.fetch_water_stops()
        if water_disruptions:
            print(f" Found {len(water_disruptions)} active water disruptions.")
            self.merge_and_save(water_disruptions)
        else:
            print(" No water disruptions found or error occurred.")
        print(" Scraper complete!")

if __name__ == "__main__":
    scraper = WaterDisruptionScraper()
    scraper.run()