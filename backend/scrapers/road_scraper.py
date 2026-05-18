import requests
import json
import os
from datetime import datetime, timezone

current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == "scrapers":
    output_path = os.path.join(os.path.dirname(current_dir), "data", "disruptions.json")
else:
    output_path = os.path.join(current_dir, "backend", "data", "disruptions.json")


def update_road_data():
    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query = """
    [out:json][timeout:25];
    (
      way["highway"="construction"]["construction"~"^(motorway|trunk|primary|secondary|tertiary|residential|unclassified)$"](42.60, 23.20, 42.75, 23.45);
    );
    out geom;
    """

    print("Изпращане на заявка към OpenStreetMap (Overpass API)...")

    try:
        headers = {"User-Agent": "SofiaCivicTech/1.0 (Student Portfolio Project)"}

        response = requests.post(
            overpass_url, data=overpass_query.encode("utf-8"), headers=headers
        )
        response.raise_for_status()

        raw_data = response.json()
        new_data = []
        scraped_at = datetime.now(tz=timezone.utc).isoformat()

        elements = raw_data.get("elements", [])
        print(f"OSM върна {len(elements)} улици в ремонт.")

        for el in elements:
            # OSM връща геометрията като списък от обекти: [{"lat": 42.1, "lon": 23.1}, ...]
            # Превръщаме ги в масив от масиви [[lat, lon], [lat, lon]], защото Leaflet обича този формат
            geometry_nodes = el.get("geometry", [])
            if not geometry_nodes:
                continue

            polyline = [[node["lat"], node["lon"]] for node in geometry_nodes]

            # За център на ремонта взимаме първата точка от линията
            center_lat = geometry_nodes[0]["lat"]
            center_lon = geometry_nodes[0]["lon"]

            # Взимаме името на улицата, ако е въведено от картографите
            tags = el.get("tags", {})
            street_name = tags.get("name", "Неизвестна улица")

            clean_item = {
                "id": f"osm_way_{el['id']}",
                "street": street_name,
                "disruption_type": "Road works",
                "description": "Пътен ремонт / Строеж",
                "start_date": "",  # OSM рядко пази начална дата
                "end_date": "",
                "latitude": float(center_lat),
                "longitude": float(center_lon),
                "scraped_at": scraped_at,
                "source": "osm_roads",
                "polyline": polyline,  # <-- ТОВА СА ЛИНИИТЕ ЗА КАРТАТА
            }

            new_data.append(clean_item)

        print(f"Успех! Обработени са {len(new_data)} пътни ремонта.")

        # --- ТВОЯТ КОД ЗА СЛИВАНЕ (MERGE) ---
        existing_data = {
            "timestamp": datetime.now().isoformat(),
            "count": 0,
            "disruptions": [],
        }

        try:
            if os.path.exists(output_path):
                with open(output_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
        except Exception as e:
            print(f"Няма стар файл, създаваме нов: {e}")

        all_disruptions = existing_data.get("disruptions", [])

        # Изтриваме старите пътища, за да не се дублират
        filtered_disruptions = [
            d
            for d in all_disruptions
            if not (
                d.get("source") == "osm_roads"
                or d.get("disruption_type") == "Road works"
                or str(d.get("id")).startswith("osm_way_")
            )
        ]

        filtered_disruptions.extend(new_data)

        existing_data["disruptions"] = filtered_disruptions
        existing_data["count"] = len(filtered_disruptions)
        existing_data["timestamp"] = datetime.now().isoformat()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        print(f"Данните са запазени в {output_path}")

    except Exception as e:
        print(f"Грешка при изтегляне на OSM данни: {e}")


if __name__ == "__main__":
    update_road_data()
