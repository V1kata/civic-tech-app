import requests
import json
import os
from datetime import datetime, timezone

# Determine the correct path for disruptions.json
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == "scrapers":
    output_path = os.path.join(os.path.dirname(current_dir), "data", "disruptions.json")
else:
    output_path = os.path.join(current_dir, "backend", "data", "disruptions.json")


def update_power_data():
    url = "https://info.ermzapad.bg/webint/vok/avplan.php"

    # Списък с известните ни райони за София (добавяй нови тук, ако откриеш)
    sofia_zones = ["SOF43", "SOF28"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    new_data = []
    scraped_at = datetime.now(tz=timezone.utc).isoformat()

    def convert_date(d_str):
        if not d_str:
            return ""
        try:
            return datetime.strptime(d_str, "%d.%m.%Y %H:%M").strftime(
                "%Y-%m-%dT%H:%M:00"
            )
        except ValueError:
            return d_str

    print(f"Изпращане на POST заявки към ЕРМ Запад за {len(sofia_zones)} района...")

    # ЗАВЪРТАМЕ ЦИКЪЛА ЗА ВСЕКИ РАЙОН
    for zone in sofia_zones:
        payload = {"action": "draw", "gm_obstina": zone, "lat": "0", "lon": "0"}

        try:
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()

            response.encoding = "utf-8-sig"
            raw_data = response.json()

            if not raw_data:
                continue  # Ако няма аварии в този район, прескачаме

            for key, item in raw_data.items():
                lat = item.get("lat")
                lon = item.get("lon")

                # Ако липсват координати или са 0/0.0, просто прескачаме този запис
                if not lat or not lon or float(lat) == 0.0 or float(lon) == 0.0:
                    continue
                clean_item = {
                    # ПРАВИМ ID-ТО УНИКАЛНО, КАТО ДОБАВЯМЕ ЗОНАТА
                    "id": f"power_{zone}_{key}",
                    "street": item.get("city_name", "София"),
                    "disruption_type": "Power outage",
                    "description": item.get("typedist", "Неизвестно"),
                    "start_date": convert_date(item.get("begin_event", "")),
                    "end_date": convert_date(item.get("end_event", "")),
                    "latitude": float(item.get("lat", 0)),
                    "longitude": float(item.get("lon", 0)),
                    "scraped_at": scraped_at,
                    "source": "electricity",
                }

                new_data.append(clean_item)

        except Exception as e:
            print(f"Грешка при изтегляне на район {zone}: {e}")

    print(f"Успех! Извлечени са общо {len(new_data)} района без ток.")

    # ТВОЯТ ПЕРФЕКТЕН КОД ЗА MERGE ОТТУК НАДОЛУ
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
        print(f"Could not load existing disruptions (will create new): {e}")

    all_disruptions = existing_data.get("disruptions", [])

    filtered_disruptions = [
        d
        for d in all_disruptions
        if not (
            d.get("source") == "electricity"
            or d.get("disruption_type") == "Power outage"
            or str(d.get("id")).startswith("power_")
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


if __name__ == "__main__":
    update_power_data()
