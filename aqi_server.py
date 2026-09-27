from flask import Flask, jsonify, send_from_directory, request
from dashboard import get_dashboard_data
import pandas as pd
import numpy as np
import os

app = Flask(__name__, static_folder=".", static_url_path="")


def make_aqi_json_safe(obj):
    """Convert pandas/numpy objects into JSON-safe Python values."""

    if isinstance(obj, pd.DataFrame):
        return [
            make_aqi_json_safe(row)
            for row in obj.to_dict(orient="records")
        ]

    if isinstance(obj, pd.Series):
        return [
            make_aqi_json_safe(x)
            for x in obj.tolist()
        ]

    if isinstance(obj, dict):
        return {
            str(k): make_aqi_json_safe(v)
            for k, v in obj.items()
        }

    if isinstance(obj, (list, tuple)):
        return [
            make_aqi_json_safe(x)
            for x in obj
        ]

    if isinstance(obj, np.integer):
        return int(obj)

    if isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)

    if isinstance(obj, np.bool_):
        return bool(obj)

    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()

    if obj is None:
        return None

    try:
        if pd.isna(obj):
            return None
    except (TypeError, ValueError):
        pass

    return obj


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/aqi/dashboard")
def aqi_dashboard():

    try:
        # Main AQI dashboard data
        data = get_dashboard_data()

        # Optional historical year filter
        year = request.args.get("year")

        if year:
            try:
                year = int(year)

                from dashboard import (
                    load_dashboard_data,
                    prepare_data,
                    get_aqi_summary,
                    get_aqi_trend,
                    get_monthly_aqi,
                    get_category_distribution,
                    get_pollutant_summary,
                    get_weather_summary,
                )

                loaded = load_dashboard_data()
                today, historical, future = prepare_data(*loaded)

                data["aqi_summary"] = get_aqi_summary(
                    historical, year
                )

                data["aqi_trend"] = get_aqi_trend(
                    historical, year
                )

                data["monthly_aqi"] = get_monthly_aqi(
                    historical, year
                )

                data["category_distribution"] = get_category_distribution(
                    historical, year
                )

                data["pollutant_summary"] = get_pollutant_summary(
                    historical, year
                )

                data["weather_summary"] = get_weather_summary(
                    historical, year
                )

            except Exception as year_error:
                print("AQI year-filter warning:", year_error)

        safe_data = make_aqi_json_safe(data)

        return jsonify(safe_data)

    except Exception as error:
        print("AQI dashboard error:", error)

        return jsonify({
            "error": str(error)
        }), 500


if __name__ == "__main__":
    print()
    print("==============================================")
    print("       VISAKHAPATNAM AQI PREDICTION")
    print("==============================================")
    print()
    print("AQI Dashboard:")
    print("http://127.0.0.1:5000")
    print()
    print("AQI Data Endpoint:")
    print("http://127.0.0.1:5000/aqi/dashboard")
    print()
    print("AQI backend running...")
    print()

    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1"
    )
