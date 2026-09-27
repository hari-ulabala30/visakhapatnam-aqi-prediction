# ================================
# CONFIG FILE
# ================================

import os



# API KEY


# API KEY
OPENWEATHER_API_KEY = os.getenv("0a39bb849a7673c7d205dc5c5fd7beb8")

# LOCATION (Vizag)
LATITUDE = 17.6868
LONGITUDE = 83.2185

# API URLs
OPENWEATHER_AIR_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# PATHS
DATASET_PATH = "Visakhapatnam_Clean_AQI_Data.csv"
MODEL_PATH = "aqi_model.pkl"

# MODEL SETTINGS
ROLLING_WINDOW = 21
FUTURE_DAYS = 7