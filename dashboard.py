import pandas as pd
import numpy as np


# ============================================================
# FILE PATHS
# ============================================================

TODAY_FILE = "today_aqi.csv"

HISTORICAL_FILE = (
    "Visakhapatnam_Clean_AQI_Data.csv"
)

FUTURE_FILE = "future_predictions.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_dashboard_data():

    today_df = pd.read_csv(TODAY_FILE)

    historical_df = pd.read_csv(HISTORICAL_FILE)

    future_df = pd.read_csv(FUTURE_FILE)

    return today_df, historical_df, future_df


# ============================================================
# CLEAN DATA
# ============================================================

def prepare_data(
    today_df,
    historical_df,
    future_df
):

    # Remove unnecessary spaces
    today_df.columns = today_df.columns.str.strip()

    historical_df.columns = (
        historical_df.columns
        .str.strip()
    )

    future_df.columns = (
        future_df.columns
        .str.strip()
    )


    # Convert dates
    today_df["date"] = pd.to_datetime(
        today_df["date"],
        dayfirst=True,
        errors="coerce"
    )

    historical_df["date"] = pd.to_datetime(
        historical_df["date"],
        dayfirst=True,
        errors="coerce"
    )


    # Numeric columns
    numeric_columns = [
        "pm25",
        "pm10",
        "no",
        "no2",
        "so2",
        "co",
        "ozone",
        "xylene",
        "temp",
        "humidity",
        "wind_speed",
        "wind_direction",
        "rainfall",
        "total_rf",
        "solar_radiation",
        "vws",
        "AQI"
    ]


    for column in numeric_columns:

        if column in today_df.columns:

            today_df[column] = pd.to_numeric(
                today_df[column],
                errors="coerce"
            )


        if column in historical_df.columns:

            historical_df[column] = pd.to_numeric(
                historical_df[column],
                errors="coerce"
            )


    future_df["predicted_aqi"] = pd.to_numeric(
        future_df["predicted_aqi"],
        errors="coerce"
    )


    return (
        today_df,
        historical_df,
        future_df
    )


# ============================================================
# CURRENT / TODAY DATA
# ============================================================

def get_current_data(today_df):

    if today_df.empty:

        return {}

    latest = today_df.iloc[-1]


    current_data = {

        "date": latest.get("date"),

        "AQI": latest.get("AQI"),

        "AQI_Category": latest.get(
            "AQI_Category"
        ),

        "PM2.5": latest.get("pm25"),

        "PM10": latest.get("pm10"),

        "NO": latest.get("no"),

        "NO2": latest.get("no2"),

        "SO2": latest.get("so2"),

        "CO": latest.get("co"),

        "Ozone": latest.get("ozone"),

        "Xylene": latest.get("xylene"),

        "Temperature": latest.get("temp"),

        "Humidity": latest.get("humidity"),

        "Wind Speed": latest.get("wind_speed"),

        "Wind Direction": latest.get(
            "wind_direction"
        ),

        "Rainfall": latest.get("rainfall"),

        "Total Rainfall": latest.get(
            "total_rf"
        ),

        "Solar Radiation": latest.get(
            "solar_radiation"
        ),

        "Vertical Wind Speed": latest.get(
            "vws"
        )
    }


    return current_data


# ============================================================
# AQI CATEGORY
# ============================================================

def get_aqi_category(aqi):

    if pd.isna(aqi):

        return "Unknown"


    if aqi <= 50:

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


# ============================================================
# AQI SUMMARY
# ============================================================

def get_aqi_summary(
    historical_df,
    year=None
):

    data = historical_df.copy()


    if year is not None:

        data = data[
            data["date"].dt.year == year
        ]


    if data.empty:

        return {

            "maximum_aqi": None,

            "minimum_aqi": None,

            "average_aqi": None,

            "median_aqi": None,

            "records": 0
        }


    return {

        "maximum_aqi": round(
            data["AQI"].max(),
            2
        ),

        "minimum_aqi": round(
            data["AQI"].min(),
            2
        ),

        "average_aqi": round(
            data["AQI"].mean(),
            2
        ),

        "median_aqi": round(
            data["AQI"].median(),
            2
        ),

        "records": len(data)
    }


# ============================================================
# AVAILABLE YEARS
# ============================================================

def get_available_years(
    historical_df
):

    years = (
        historical_df["date"]
        .dt.year
        .dropna()
        .unique()
    )

    return sorted(
        years.astype(int).tolist()
    )


# ============================================================
# DAILY AQI TREND
# ============================================================

def get_aqi_trend(
    historical_df,
    year=None
):

    data = historical_df.copy()


    if year is not None:

        data = data[
            data["date"].dt.year == year
        ]


    trend = (
        data[
            ["date", "AQI"]
        ]
        .dropna()
        .sort_values("date")
        .reset_index(drop=True)
    )


    return trend


# ============================================================
# MONTHLY AQI
# ============================================================

def get_monthly_aqi(
    historical_df,
    year=None
):

    data = historical_df.copy()


    if year is not None:

        data = data[
            data["date"].dt.year == year
        ]


    data["month_number"] = (
        data["date"].dt.month
    )

    data["month"] = (
        data["date"]
        .dt.month_name()
    )


    monthly = (
        data
        .groupby(
            [
                "month_number",
                "month"
            ],
            as_index=False
        )["AQI"]
        .mean()
    )


    monthly["AQI"] = monthly["AQI"].round(2)


    return monthly.sort_values(
        "month_number"
    )


# ============================================================
# AQI CATEGORY DISTRIBUTION
# ============================================================

def get_category_distribution(
    historical_df,
    year=None
):

    data = historical_df.copy()


    if year is not None:

        data = data[
            data["date"].dt.year == year
        ]


    if "AQI_Category" in data.columns:

        distribution = (
            data["AQI_Category"]
            .value_counts()
            .reset_index()
        )

        distribution.columns = [
            "AQI_Category",
            "Count"
        ]

    else:

        data["AQI_Category"] = (
            data["AQI"]
            .apply(get_aqi_category)
        )


        distribution = (
            data["AQI_Category"]
            .value_counts()
            .reset_index()
        )

        distribution.columns = [
            "AQI_Category",
            "Count"
        ]


    return distribution


# ============================================================
# POLLUTANT SUMMARY
# ============================================================

def get_pollutant_summary(
    historical_df,
    year=None
):

    data = historical_df.copy()


    if year is not None:

        data = data[
            data["date"].dt.year == year
        ]


    pollutants = {

        "PM2.5": "pm25",

        "PM10": "pm10",

        "NO": "no",

        "NO2": "no2",

        "SO2": "so2",

        "CO": "co",

        "Ozone": "ozone",

        "Xylene": "xylene"
    }


    results = []


    for name, column in pollutants.items():

        if column in data.columns:

            results.append({

                "Pollutant": name,

                "Average": round(
                    data[column].mean(),
                    2
                ),

                "Minimum": round(
                    data[column].min(),
                    2
                ),

                "Maximum": round(
                    data[column].max(),
                    2
                )
            })


    return pd.DataFrame(results)


# ============================================================
# POLLUTANT TREND
# ============================================================

def get_pollutant_trend(
    historical_df,
    pollutant,
    year=None
):

    data = historical_df.copy()


    if year is not None:

        data = data[
            data["date"].dt.year == year
        ]


    pollutant_columns = {

        "PM2.5": "pm25",

        "PM10": "pm10",

        "NO": "no",

        "NO2": "no2",

        "SO2": "so2",

        "CO": "co",

        "Ozone": "ozone",

        "Xylene": "xylene"
    }


    column = pollutant_columns.get(
        pollutant,
        pollutant
    )


    if column not in data.columns:

        return pd.DataFrame()


    trend = data[
        ["date", column]
    ].copy()


    trend = trend.rename(
        columns={
            column: pollutant
        }
    )


    return trend.sort_values(
        "date"
    ).reset_index(drop=True)


# ============================================================
# WEATHER SUMMARY
# ============================================================

def get_weather_summary(
    historical_df,
    year=None
):

    data = historical_df.copy()


    if year is not None:

        data = data[
            data["date"].dt.year == year
        ]


    weather_columns = {

        "Temperature": "temp",

        "Humidity": "humidity",

        "Wind Speed": "wind_speed",

        "Rainfall": "rainfall",

        "Total Rainfall": "total_rf",

        "Solar Radiation":
            "solar_radiation",

        "Vertical Wind Speed":
            "vws"
    }


    results = []


    for name, column in weather_columns.items():

        if column in data.columns:

            results.append({

                "Parameter": name,

                "Average": round(
                    data[column].mean(),
                    2
                ),

                "Minimum": round(
                    data[column].min(),
                    2
                ),

                "Maximum": round(
                    data[column].max(),
                    2
                )
            })


    return pd.DataFrame(results)


# ============================================================
# MONTHLY POLLUTANT ANALYSIS
# ============================================================

def get_monthly_pollutant_analysis(
    historical_df,
    pollutant,
    year=None
):

    data = historical_df.copy()


    if year is not None:

        data = data[
            data["date"].dt.year == year
        ]


    pollutant_columns = {

        "PM2.5": "pm25",

        "PM10": "pm10",

        "NO2": "no2",

        "SO2": "so2",

        "CO": "co",

        "Ozone": "ozone"
    }


    column = pollutant_columns.get(
        pollutant,
        pollutant
    )


    if column not in data.columns:

        return pd.DataFrame()


    data["month_number"] = (
        data["date"].dt.month
    )

    data["month"] = (
        data["date"]
        .dt.month_name()
    )


    result = (
        data
        .groupby(
            [
                "month_number",
                "month"
            ],
            as_index=False
        )[column]
        .mean()
    )


    result = result.rename(
        columns={
            column: pollutant
        }
    )


    result[pollutant] = (
        result[pollutant]
        .round(2)
    )


    return result.sort_values(
        "month_number"
    )


# ============================================================
# FUTURE AQI PREDICTIONS
# ============================================================

def get_future_predictions(
    future_df
):

    predictions = future_df.copy()


    predictions["predicted_aqi"] = (
        predictions["predicted_aqi"]
        .round(2)
    )


    predictions["category"] = (
        predictions["predicted_aqi"]
        .apply(get_aqi_category)
    )


    return predictions


# ============================================================
# FUTURE PREDICTION SUMMARY
# ============================================================

def get_future_summary(
    future_df
):

    if future_df.empty:

        return {

            "maximum": None,

            "minimum": None,

            "average": None,

            "highest_day": None,

            "lowest_day": None
        }


    maximum = future_df[
        "predicted_aqi"
    ].max()


    minimum = future_df[
        "predicted_aqi"
    ].min()


    average = future_df[
        "predicted_aqi"
    ].mean()


    highest_index = future_df[
        "predicted_aqi"
    ].idxmax()


    lowest_index = future_df[
        "predicted_aqi"
    ].idxmin()


    return {

        "maximum": round(
            maximum,
            2
        ),

        "minimum": round(
            minimum,
            2
        ),

        "average": round(
            average,
            2
        ),

        "highest_day": future_df.loc[
            highest_index,
            "day"
        ],

        "lowest_day": future_df.loc[
            lowest_index,
            "day"
        ]
    }


# ============================================================
# HISTORICAL + FUTURE AQI
# ============================================================

def get_historical_future_comparison(
    historical_df,
    future_df,
    recent_days=30
):

    historical = (
        historical_df
        .sort_values("date")
        .tail(recent_days)
        .copy()
    )


    historical_result = pd.DataFrame({

        "date": historical["date"],

        "AQI": historical["AQI"],

        "type": "Historical"
    })


    last_date = historical[
        "date"
    ].max()


    future_dates = pd.date_range(

        start=last_date
        + pd.Timedelta(days=1),

        periods=len(future_df),

        freq="D"
    )


    future_result = pd.DataFrame({

        "date": future_dates,

        "AQI": future_df[
            "predicted_aqi"
        ].values,

        "type": "Predicted"
    })


    comparison = pd.concat(
        [
            historical_result,
            future_result
        ],
        ignore_index=True
    )


    return comparison


# ============================================================
# AQI CHANGE
# ============================================================

def get_aqi_change(
    today_aqi,
    predicted_aqi
):

    if (
        today_aqi is None
        or predicted_aqi is None
    ):

        return None


    change = (
        predicted_aqi
        - today_aqi
    )


    percentage = (
        change
        / today_aqi
        * 100
    ) if today_aqi != 0 else None


    return {

        "absolute_change": round(
            change,
            2
        ),

        "percentage_change": (
            round(
                percentage,
                2
            )
            if percentage is not None
            else None
        ),

        "direction": (
            "Increase"
            if change > 0
            else "Decrease"
            if change < 0
            else "No Change"
        )
    }


# ============================================================
# COMPLETE DASHBOARD DATA
# ============================================================

def get_dashboard_data():

    today_df, historical_df, future_df = (
        load_dashboard_data()
    )


    today_df, historical_df, future_df = (
        prepare_data(
            today_df,
            historical_df,
            future_df
        )
    )


    current = get_current_data(
        today_df
    )


    future_predictions = (
        get_future_predictions(
            future_df
        )
    )


    future_summary = (
        get_future_summary(
            future_df
        )
    )


    first_prediction = None

    if not future_df.empty:

        first_prediction = future_df[
            "predicted_aqi"
        ].iloc[0]


    aqi_change = get_aqi_change(
        current.get("AQI"),
        first_prediction
    )


    return {

        "current": current,

        "historical": historical_df,

        "future": future_predictions,

        "years": get_available_years(
            historical_df
        ),

        "aqi_summary": get_aqi_summary(
            historical_df
        ),

        "aqi_trend": get_aqi_trend(
            historical_df
        ),

        "monthly_aqi": get_monthly_aqi(
            historical_df
        ),

        "category_distribution":
            get_category_distribution(
                historical_df
            ),

        "pollutant_summary":
            get_pollutant_summary(
                historical_df
            ),

        "weather_summary":
            get_weather_summary(
                historical_df
            ),

        "historical_future":
            get_historical_future_comparison(
                historical_df,
                future_df
            ),

        "future_summary":
            future_summary,

        "aqi_change":
            aqi_change
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    dashboard = get_dashboard_data()


    print("\n===================================")
    print("VISAKHAPATNAM AQI DASHBOARD DATA")
    print("===================================")


    print("\nCURRENT AQI")

    print(
        dashboard["current"]
    )


    print("\nAQI SUMMARY")

    print(
        dashboard["aqi_summary"]
    )


    print("\nFUTURE PREDICTIONS")

    print(
        dashboard["future"]
    )


    print("\nFUTURE SUMMARY")

    print(
        dashboard["future_summary"]
    )


    print("\nAQI CHANGE")

    print(
        dashboard["aqi_change"]
    )


    print("\nPOLLUTANT SUMMARY")

    print(
        dashboard["pollutant_summary"]
    )


    print("\nWEATHER SUMMARY")

    print(
        dashboard["weather_summary"]
    )