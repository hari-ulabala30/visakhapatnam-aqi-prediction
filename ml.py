# =====================================
# 1. IMPORT LIBRARIES
# =====================================
import pandas as pd
import numpy as np
import joblib
import os

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from xgboost import XGBRegressor

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from config import DATASET_PATH
from fetch_air import fetch_air_quality
from fetch_wether import fetch_weather
from update_set import update_dataset
from config import MODEL_PATH


print("Updating dataset...")
update_dataset()



# =====================================
# 2. LOAD DATA
# =====================================
print("Loading dataset...")
df = pd.read_csv(DATASET_PATH)

df.columns = df.columns.str.strip().str.lower()
df['date'] = pd.to_datetime(df['date'], dayfirst=True)
df = df.sort_values('date')

print("Data loaded:", df.shape)

# =====================================
# 3. FEATURE ENGINEERING
# =====================================

# -------- Lag Features --------
df['aqi_lag1'] = df['aqi'].shift(1)
df['aqi_lag2'] = df['aqi'].shift(2)
df['aqi_lag3'] = df['aqi'].shift(3)
df['aqi_lag7'] = df['aqi'].shift(7)
df['aqi_lag14'] = df['aqi'].shift(14)
df['aqi_lag21'] = df['aqi'].shift(21)

df['pm25_lag1'] = df['pm25'].shift(1)
df['pm25_lag3'] = df['pm25'].shift(3)
df['pm10_lag3'] = df['pm10'].shift(3)

# -------- Rolling --------
df['aqi_roll3'] = df['aqi'].rolling(3).mean()
df['aqi_roll7'] = df['aqi'].rolling(7).mean()
df['aqi_roll14'] = df['aqi'].rolling(14).mean()
df['aqi_roll21'] = df['aqi'].rolling(21).mean()

# -------- Time Features --------
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day

# -------- Interaction Features --------
df['temp_humidity'] = df['temp'] * df['humidity']
df['pm_ratio'] = df['pm25'] / (df['pm10'] + 1)
df['rain_wind'] = df['rainfall'] * df['wind_speed']


# Fill missing values smartly
df = df.ffill()
df = df.bfill()

# Then drop if still any
df = df.dropna()

print("After feature engineering:", df.shape)

# =====================================
# 4. TIME SPLIT (80/10/10)
# =====================================
train_size = int(len(df) * 0.8)
val_size = int(len(df) * 0.1)

train = df[:train_size]
val = df[train_size:train_size + val_size]
test = df[train_size + val_size:]

# =====================================
# 5. FEATURES
# =====================================
features = [
    'aqi_lag1','aqi_lag2','aqi_lag3',
    'aqi_lag7','aqi_lag14','aqi_lag21',
    'aqi_roll3','aqi_roll7','aqi_roll14','aqi_roll21'
]

# =====================================
# 6. MODELS
# =====================================
lr = LinearRegression()

rf = RandomForestRegressor(
    n_estimators=600,
    max_depth=20,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

et = ExtraTreesRegressor(
    n_estimators=500,
    max_depth=20,
    random_state=42,
    n_jobs=-1
)

xgb = XGBRegressor(
    n_estimators=800,
    learning_rate=0.02,
    max_depth=8,
    min_child_weight=3,
    gamma=0.1,
    subsample=0.9,
    colsample_bytree=0.9,
    reg_alpha=0.1,
    reg_lambda=1,
    random_state=42
)

models = {
    "lr": lr,
    "rf": rf,
    "et": et,
    "xgb": xgb
}

# =====================================
# MODEL RETRAINING SCHEDULE
# =====================================
MODEL_RETRAIN_DAYS = 30

retrain_model = True
model_age_days = None

if os.path.exists(MODEL_PATH):

    model_age_days = (
        pd.Timestamp.now()
        - pd.to_datetime(
            os.path.getmtime(MODEL_PATH),
            unit="s"
        )
    ).total_seconds() / 86400

    retrain_model = model_age_days >= MODEL_RETRAIN_DAYS

    print(
        f"Existing model age: {model_age_days:.1f} days"
    )

    if retrain_model:
        print("Model is 30 days old or more. Retraining required.")

    else:
        print("Model is less than 30 days old. Using existing model.")


if not retrain_model:

    try:

        saved_model = joblib.load(MODEL_PATH)

        models = saved_model["models"]
        weights = saved_model["weights"]
        features = saved_model["features"]

        validation_mae = saved_model.get("validation_mae")
        validation_mse = saved_model.get("validation_mse")
        validation_r2 = saved_model.get("validation_r2")

        test_mae = saved_model.get("test_mae")
        test_mse = saved_model.get("test_mse")
        test_r2 = saved_model.get("test_r2")

        print("Existing model loaded successfully.")

        if validation_mae is not None:
            print("\nSAVED VALIDATION RESULTS")
            print("MAE:", validation_mae)
            print("MSE:", validation_mse)
            print("R2 :", validation_r2)

        if test_mae is not None:
            print("\nSAVED TEST RESULTS")
            print("MAE:", test_mae)
            print("MSE:", test_mse)
            print("R2 :", test_r2)

        print("Existing model loaded successfully.")

    except Exception as error:

        print(
            "Existing model could not be loaded."
        )

        print("Error:", error)
        print("Retraining model now.")

        retrain_model = True


if retrain_model:

    # =====================================
    # 7. TRAIN + VALIDATION
    # =====================================
    print("\nTraining models...")

    X_train = train[features]
    y_train = train['aqi']

    X_val = val[features]
    y_val = val['aqi']

    weights = {}
    predictions = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_val)
        score = r2_score(y_val, pred)

        weights[name] = max(score, 0.01)  # avoid zero
        predictions[name] = pred

    # Normalize weights
    total = sum(weights.values())
    for k in weights:
        weights[k] /= total

    print("\nModel Weights:")
    print(weights)

    # Ensemble prediction
    val_preds = sum(weights[m] * predictions[m] for m in models)
    print("\nVALIDATION RESULTS")

    validation_mae = mean_absolute_error(y_val, val_preds)
    validation_mse = mean_squared_error(y_val, val_preds)
    validation_r2 = r2_score(y_val, val_preds)

    print("MAE:", validation_mae)
    print("MSE:", validation_mse)
    print("R2 :", validation_r2)

    

    # =====================================
    # 8. TEST
    # =====================================
    X_test = test[features]
    y_test = test['aqi']

    test_preds = sum(weights[m] * models[m].predict(X_test) for m in models)

    print("\nTEST RESULTS")
    print("\nTEST RESULTS")

    test_mae = mean_absolute_error(y_test, test_preds)
    test_mse = mean_squared_error(y_test, test_preds)
    test_r2 = r2_score(y_test, test_preds)

    print("MAE:", test_mae)
    print("MSE:", test_mse)
    print("R2 :", test_r2)


# =====================================
# =====================================
# 9. FUTURE PREDICTION (FINAL FIXED)
# =====================================

# =====================================
# FINAL CORRECT FUTURE PREDICTION
# =====================================

future_days = 7
future_preds = []

# Take last known values
aqi_history = list(df['aqi'].iloc[-21:])  # last 21 real values

last_date = pd.to_datetime(df['date'].iloc[-1], dayfirst=True)

for i in range(future_days):

    temp_df = df.iloc[-1:].copy()

    # ✅ Use updated history
    temp_df['aqi_lag1'] = aqi_history[-1]
    temp_df['aqi_lag2'] = aqi_history[-2]
    temp_df['aqi_lag3'] = aqi_history[-3]
    temp_df['aqi_lag7'] = aqi_history[-7]
    temp_df['aqi_lag14'] = aqi_history[-14]
    temp_df['aqi_lag21'] = aqi_history[-21]

    temp_df['aqi_roll3'] = sum(aqi_history[-3:]) / 3
    temp_df['aqi_roll7'] = sum(aqi_history[-7:]) / 7
    temp_df['aqi_roll14'] = sum(aqi_history[-14:]) / 14
    temp_df['aqi_roll21'] = sum(aqi_history[-21:]) / 21

    X_input = temp_df[features]

    raw_pred = sum(weights[m] * models[m].predict(X_input)[0] for m in models)

# 🔥 smoothing
    pred = (aqi_history[-1] * 0.7) + (raw_pred * 0.3)

    future_preds.append(pred)

    # 🔥 Update history CORRECTLY
    aqi_history.pop(0)
    aqi_history.append(pred)

print("\nFUTURE AQI:")
for i, val in enumerate(future_preds, 1):
    print(f"Day {i}: {val:.2f}")

from datetime import datetime

# Save predictions
future_df_save = pd.DataFrame({
    "day": [f"Day {i}" for i in range(1, 8)],
    "predicted_aqi": future_preds
})

future_df_save.to_csv("future_predictions.csv", index=False)

# Log
with open("logs.txt", "a") as f:
    f.write(f"{datetime.now()} - Future predictions saved\n")    
if retrain_model:

    # =====================================
    # 10. FINAL TRAIN (FULL DATA)
    # =====================================
    print("\nTraining final model...")

    X_final = df[features]
    y_final = df['aqi']

    for model in models.values():
        model.fit(X_final, y_final)

    final_model = {
    "models": models,
    "weights": weights,
    "features": features,

    "validation_mae": validation_mae,
    "validation_mse": validation_mse,
    "validation_r2": validation_r2,

    "test_mae": test_mae,
    "test_mse": test_mse,
    "test_r2": test_r2
}


    joblib.dump(final_model, MODEL_PATH)


    print("Model saved successfully!")



    with open("logs.txt", "a") as f:
        f.write(f"{datetime.now()} - Model trained and saved\n")
