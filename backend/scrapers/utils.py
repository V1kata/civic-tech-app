"""
Utility functions for Civic Tech App scraper
"""

import requests
from typing import Dict, Optional, List
import time


def safe_get_text(element, selector: str, default: str = "") -> str:
    """
    Safely extract text from an HTML element.
    
    Args:
        element: BeautifulSoup element
        selector: CSS selector
        default: Default value if not found
    
    Returns:
        Extracted text or default value
    """
    try:
        found = element.select_one(selector)
        return found.get_text(strip=True) if found else default
    except Exception:
        return default


def is_valid_date(date_string: str) -> bool:
    """
    Check if a string is a valid date format.
    
    Args:
        date_string: Date string to validate
    
    Returns:
        True if valid, False otherwise
    """
    from datetime import datetime
    date_formats = [
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
    ]
    
    for fmt in date_formats:
        try:
            datetime.strptime(date_string, fmt)
            return True
        except ValueError:
            continue
    
    return False


def is_valid_coordinates(lat: float, lon: float) -> bool:
    """
    Check if coordinates are valid.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        True if valid, False otherwise
    """
    try:
        return -90 <= float(lat) <= 90 and -180 <= float(lon) <= 180
    except (TypeError, ValueError):
        return False


def remove_duplicates(disruptions: List[Dict]) -> List[Dict]:
    """
    Remove duplicate disruptions based on street + type.
    Keeps the most recent entry.
    
    Args:
        disruptions: List of disruption dictionaries
    
    Returns:
        List of disruptions with duplicates removed
    """
    seen = {}
    
    for disruption in sorted(disruptions, key=lambda x: x.get("scraped_at", ""), reverse=True):
        key = (disruption["street"], disruption["disruption_type"])
        if key not in seen:
            seen[key] = disruption
    
    return list(seen.values())


def validate_disruption(disruption: Dict) -> bool:
    """
    Validate that a disruption has all required fields.
    
    Args:
        disruption: Disruption dictionary
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["street", "disruption_type", "start_date", "end_date", "latitude", "longitude"]
    
    # Check all required fields exist
    if not all(field in disruption for field in required_fields):
        return False
    
    # Check types
    if not isinstance(disruption["street"], str) or not disruption["street"].strip():
        return False
    
    if not isinstance(disruption["disruption_type"], str) or not disruption["disruption_type"].strip():
        return False
    
    # Check dates
    if not isinstance(disruption["start_date"], str) or not disruption["start_date"].strip():
        return False
    
    if not isinstance(disruption["end_date"], str) or not disruption["end_date"].strip():
        return False
    
    # Check coordinates
    try:
        lat = float(disruption["latitude"])
        lon = float(disruption["longitude"])
        if not is_valid_coordinates(lat, lon):
            return False
    except (TypeError, ValueError):
        return False
    
    return True


def retry_request(url: str, max_retries: int = 3, delay: int = 2, **kwargs) -> Optional[requests.Response]:
    """
    Make HTTP request with retry logic.
    
    Args:
        url: Target URL
        max_retries: Maximum retry attempts
        delay: Delay between retries (seconds)
        **kwargs: Additional requests.get() parameters
    
    Returns:
        Response object or None if failed
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                print(f"⚠️  Attempt {attempt + 1}/{max_retries} failed. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"❌ Failed after {max_retries} attempts: {str(e)}")
                return None
    
    return None


if __name__ == "__main__":
    # Test functions
    print("✅ Utility functions loaded successfully")
