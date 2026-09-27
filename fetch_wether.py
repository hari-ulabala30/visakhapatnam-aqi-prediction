import requests
from config import LATITUDE, LONGITUDE, OPEN_METEO_URL


def fetch_weather():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_direction_10m",
            "rain",
            "shortwave_radiation"
        ])
    }

    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=20)
        response.raise_for_status()

        data = response.json()["current"]

        weather = {
            "temp": data["temperature_2m"],
            "humidity": data["relative_humidity_2m"],
            "wind_speed": data["wind_speed_10m"],
            "wind_direction": data["wind_direction_10m"],
            "rainfall": data["rain"],
            "total_rf": data["rain"],   # duplicate mapping
            "solar_radiation": data["shortwave_radiation"],
            "vws": data["wind_speed_10m"]  # approximate
        }

        return weather

    except Exception as e:
        print("Weather API Error:", e)
        return None