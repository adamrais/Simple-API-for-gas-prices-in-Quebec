import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

df = pd.read_csv(os.path.join(DATA_DIR, "dataset_v3.csv"))
df = df.sort_values("date").reset_index(drop=True)

prix  = df["prix_pompe"].values
N_LAGS = 4

rows = []
for i in range(N_LAGS, len(prix)):
    row = [prix[i - j] for j in range(1, N_LAGS + 1)]
    row.append(prix[i])
    rows.append(row)

cols = [f"lag_{j}" for j in range(1, N_LAGS + 1)] + ["target"]
data = pd.DataFrame(rows, columns=cols)

X = data[[f"lag_{j}" for j in range(1, N_LAGS + 1)]].values
y = data["target"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

print(f"R² train = {r2_score(y_train, model.predict(X_train)):.4f}")
print(f"R² test  = {r2_score(y_test,  model.predict(X_test)):.4f}")
print(f"MAE test = {mean_absolute_error(y_test, model.predict(X_test)):.2f} ¢/L")

model_ar_path  = os.path.join(MODEL_DIR, "model_ar.pkl")
last_known_path = os.path.join(MODEL_DIR, "last_known.pkl")

with open(model_ar_path, "wb") as f:
    pickle.dump(model, f)

last_known = prix[-N_LAGS:].tolist()
with open(last_known_path, "wb") as f:
    pickle.dump(last_known, f)

print(f"\nmodel_ar.pkl + last_known.pkl sauvegardés dans {MODEL_DIR}")
