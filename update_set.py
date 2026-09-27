import pandas as pd
from datetime import datetime

from fetch_air import fetch_air_quality
from fetch_wether import fetch_weather
from config import DATASET_PATH


# -----------------------------
# AQI CALCULATION
# -----------------------------

def calculate_subindex(Cp, breakpoints):
    for bp in breakpoints:
        if bp[0] <= Cp <= bp[1]:
            BLO, BHI, ILO, IHI = bp
            return ((IHI - ILO) / (BHI - BLO)) * (Cp - BLO) + ILO
    return 0


def calculate_aqi(pm25, pm10, no2, so2, co, o3):

    pm25_bp = [
        (0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200),
        (91, 120, 201, 300), (121, 250, 301, 400), (251, 500, 401, 500)
    ]

    pm10_bp = [
        (0, 50, 0, 50), (51, 100, 51, 100), (101, 250, 101, 200),
        (251, 350, 201, 300), (351, 430, 301, 400), (431, 600, 401, 500)
    ]

    no2_bp = [
        (0, 40, 0, 50), (41, 80, 51, 100), (81, 180, 101, 200),
        (181, 280, 201, 300), (281, 400, 301, 400), (401, 1000, 401, 500)
    ]

    so2_bp = [
        (0, 40, 0, 50), (41, 80, 51, 100), (81, 380, 101, 200),
        (381, 800, 201, 300), (801, 1600, 301, 400), (1601, 2000, 401, 500)
    ]

    co_bp = [
        (0, 1, 0, 50), (1.1, 2, 51, 100), (2.1, 10, 101, 200),
        (10.1, 17, 201, 300), (17.1, 34, 301, 400), (34.1, 50, 401, 500)
    ]

    o3_bp = [
        (0, 50, 0, 50), (51, 100, 51, 100), (101, 168, 101, 200),
        (169, 208, 201, 300), (209, 748, 301, 400), (749, 1000, 401, 500)
    ]

    sub_indices = []

    if pm25 is not None:
        sub_indices.append(calculate_subindex(pm25, pm25_bp))
    if pm10 is not None:
        sub_indices.append(calculate_subindex(pm10, pm10_bp))
    if no2 is not None:
        sub_indices.append(calculate_subindex(no2, no2_bp))
    if so2 is not None:
        sub_indices.append(calculate_subindex(so2, so2_bp))
    if co is not None:
        sub_indices.append(calculate_subindex(co, co_bp))
    if o3 is not None:
        sub_indices.append(calculate_subindex(o3, o3_bp))

    return round(max(sub_indices)) if sub_indices else None


# -----------------------------
# AQI CATEGORY
# -----------------------------

def get_aqi_category(aqi):
    if aqi is None:
        return None
    elif aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"


# -----------------------------
# MAIN FUNCTION
# -----------------------------

def update_dataset():

    print("Fetching API data...")

    air = fetch_air_quality()
    weather = fetch_weather()

    if air is None or weather is None:
        print("API failed. Dataset not updated.")
        return

    today_data = {**air, **weather}
    today_data["date"] = datetime.now().strftime("%d-%m-%Y")

    pm25 = air.get("pm25")
    pm10 = air.get("pm10")
    no2 = air.get("no2")
    so2 = air.get("so2")
    co = air.get("co") / 1000   # ✅ convert µg/m³ → mg/m³
    o3 = air.get("o3")

    today_data["ozone"] = o3

    aqi = calculate_aqi(pm25, pm10, no2, so2, co, o3)

    today_data["AQI"] = aqi
    
    today_data["AQI_Category"] = get_aqi_category(aqi)

    print("Loading dataset...")

    df = pd.read_csv(DATASET_PATH)
    df["date"] = df["date"].astype(str)

    if today_data["date"] in df["date"].values:
        print("Today's data already exists in historical dataset. No duplicate row added.")

    else:
        # Add new row
        new_row = pd.DataFrame([today_data])
        df = pd.concat([df, new_row], ignore_index=True)
        print("New today's data added to historical dataset.")
    # Save historical dataset
    df.to_csv(DATASET_PATH, index=False)

    print("Historical dataset saved successfully!")


    # Always update today's latest API data
    pd.DataFrame([today_data]).to_csv(
        "today_aqi.csv",
        index=False
    )

    print("Today's latest AQI data saved successfully!")

    # Log
    with open("logs.txt", "a") as f:
        f.write(f"{datetime.now()} - Today's AQI saved\n")

    

  
# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    update_dataset()

   

    with open("logs.txt", "a") as f:
        f.write(f"{datetime.now()} - Dataset updated successfully\n")
