"""
Road Repairs Scraper - Civic Tech App Backend
Scrapes public data about road disruptions in Sofia, Bulgaria
Output: JSON file with street names, coordinates, and disruption details
"""

import json
import requests
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
import time

# For geocoding (converting addresses to lat/lon)
try:
    # pyrefly: ignore [missing-import]
    from geopy.geocoders import Nominatim
except ImportError:
    print("Install geopy: pip install geopy")
    Nominatim = None

# Configuration
CONFIG = {
    "output_file": "data/disruptions.json",
    "geocoder_timeout": 10,
    "request_timeout": 10,
    "request_delay": 1,  # seconds between requests (respect rate limits)
    "sofia_center": {"lat": 42.6977, "lon": 23.3219}
}


class RoadsDisruptionScraper:
    """
    Base scraper for road disruptions.
    
    In production, subclass this for each utility provider:
    - Sofia Water Supply Company (SVP)
    - Public Works Department
    - etc.
    """
    
    def __init__(self):
        self.disruptions: List[Dict[str, Any]] = []
        self.geocoder = Nominatim(user_agent="civic_tech_app") if Nominatim else None
    
    def geocode_address(self, address: str, city: str = "Sofia") -> Dict[str, float]:
        """
        Convert street address to latitude/longitude.
        
        Args:
            address: Street name or full address
            city: City name (default: Sofia)
        
        Returns:
            {"lat": float, "lon": float} or {"lat": None, "lon": None} if failed
        """
        if not self.geocoder:
            return {"lat": None, "lon": None}
        
        try:
            full_address = f"{address}, {city}, Bulgaria"
            location = self.geocoder.geocode(full_address, timeout=CONFIG["geocoder_timeout"])
            
            if location:
                return {"lat": location.latitude, "lon": location.longitude}
            else:
                print(f"⚠️  Could not geocode: {full_address}")
                return {"lat": None, "lon": None}
        
        except Exception as e:
            print(f"❌ Geocoding error for '{address}': {str(e)}")
            return {"lat": None, "lon": None}
    
    def fetch_html(self, url: str) -> str:
        """
        Fetch HTML content from a URL.
        
        Args:
            url: Target URL
        
        Returns:
            HTML content as string, or empty string if failed
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=CONFIG["request_timeout"])
            response.raise_for_status()
            return response.text
        
        except requests.RequestException as e:
            print(f"❌ Failed to fetch {url}: {str(e)}")
            return ""
    
    def parse_html_table(self, html: str) -> List[Dict[str, str]]:
        """
        Parse HTML table into list of dictionaries.
        This is a DEMO function - adapt based on actual website structure.
        
        Expected HTML format:
        <table>
          <tr>
            <td>Vasil Levski Blvd</td>
            <td>Road works</td>
            <td>2024-05-15</td>
            <td>2024-05-20</td>
          </tr>
        </table>
        """
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            rows = []
            
            # Adjust selectors based on actual website structure
            for tr in soup.find_all("tr")[1:]:  # Skip header row
                cells = tr.find_all("td")
                if len(cells) >= 4:
                    rows.append({
                        "street": cells[0].text.strip(),
                        "type": cells[1].text.strip(),
                        "start_date": cells[2].text.strip(),
                        "end_date": cells[3].text.strip(),
                    })
            
            return rows
        
        except Exception as e:
            print(f"❌ HTML parsing error: {str(e)}")
            return []
    
    def scrape_demo_data(self) -> List[Dict[str, Any]]:
        """
        DEMO: Create sample data for testing.
        In production, replace this with actual scraping logic.
        """
        demo_disruptions = [
            {
                "street": "Vasil Levski Blvd",
                "type": "Road works",
                "start_date": "2024-05-15",
                "end_date": "2024-05-20",
            },
            {
                "street": "Tsar Osvobodit Blvd",
                "type": "Water main repair",
                "start_date": "2024-05-18",
                "end_date": "2024-05-25",
            },
            {
                "street": "Vitosha Blvd",
                "type": "Road works",
                "start_date": "2024-05-10",
                "end_date": "2024-05-12",
            },
        ]
        return demo_disruptions
    
    def process_disruptions(self, raw_data: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Enrich raw data with coordinates and metadata.
        
        Args:
            raw_data: List of disruptions from parser
        
        Returns:
            List of processed disruptions with coordinates
        """
        processed = []
        
        for item in raw_data:
            # Geocode the address
            coords = self.geocode_address(item["street"])
            
            # Skip if geocoding failed (optional - can use Sofia center as fallback)
            if coords["lat"] is None:
                coords = CONFIG["sofia_center"]
                print(f"⚠️  Using Sofia center for: {item['street']}")
            
            processed.append({
                "id": f"{item['street'].replace(' ', '_').lower()}_{datetime.now().timestamp()}",
                "street": item["street"],
                "disruption_type": item["type"],
                "start_date": item["start_date"],
                "end_date": item["end_date"],
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "scraped_at": datetime.now().isoformat(),
            })
            
            # Respect rate limits
            time.sleep(CONFIG["request_delay"])
        
        return processed
    
    def save_to_json(self, data: List[Dict[str, Any]]) -> None:
        """
        Save processed disruptions to JSON file.
        
        Args:
            data: List of disruptions
        """
        try:
            output = {
                "timestamp": datetime.now().isoformat(),
                "count": len(data),
                "disruptions": data,
            }
            
            with open(CONFIG["output_file"], "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(data)} disruptions to {CONFIG['output_file']}")
        
        except Exception as e:
            print(f"❌ Failed to save JSON: {str(e)}")
    
    def run(self, use_demo: bool = True) -> None:
        """
        Main scraper execution.
        
        Args:
            use_demo: If True, use demo data; if False, fetch from real websites
        """
        print("🚀 Starting Road Disruptions Scraper...")
        
        # Get data
        if use_demo:
            print("📋 Using demo data for testing...")
            raw_data = self.scrape_demo_data()
        else:
            print("🌐 Fetching from live websites...")
            # TODO: Replace with actual URL scraping
            raw_data = self.scrape_demo_data()
        
        # Process data
        print("🔄 Processing data (geocoding addresses)...")
        processed = self.process_disruptions(raw_data)
        
        # Save
        self.save_to_json(processed)
        print("✅ Scraper complete!")


if __name__ == "__main__":
    scraper = RoadsDisruptionScraper()
    scraper.run(use_demo=True)
