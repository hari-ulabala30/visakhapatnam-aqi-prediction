import requests
from config import OPENWEATHER_API_KEY, LATITUDE, LONGITUDE, OPENWEATHER_AIR_URL


print("API KEY:", OPENWEATHER_API_KEY)

def fetch_air_quality():
    try:
        # ✅ Proper params (API key included)
        params = {
            "lat": LATITUDE,
            "lon": LONGITUDE,
            "appid": OPENWEATHER_API_KEY
        }

        # ✅ API request
        response = requests.get(OPENWEATHER_AIR_URL, params=params, timeout=20)
        response.raise_for_status()

        # ✅ Extract data safely
        json_data = response.json()

        if "list" not in json_data or len(json_data["list"]) == 0:
            print("Invalid API response")
            return None

        data = json_data["list"][0]["components"]

        # ✅ Pollutants mapping (with fixes)
        pollutants = {
            "pm25": data.get("pm2_5"),
            "pm10": data.get("pm10"),
            "no": data.get("no"),
            "no2": data.get("no2"),
            "so2": data.get("so2"),
            "co": data.get("co") / 1000 if data.get("co") is not None else None,  # ✅ FIX
            "o3": data.get("o3"),
            "xylene": 0  # Not provided by API
        }

        # ✅ Debug (optional - remove later)
        print("Fetched Air Data:", pollutants)

        return pollutants

    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e)
    except requests.exceptions.ConnectionError:
        print("Connection Error. Check internet.")
    except requests.exceptions.Timeout:
        print("Request Timeout.")
    except Exception as e:
        print("Air API Error:", e)

    return None