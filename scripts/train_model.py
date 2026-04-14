import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

df = pd.read_csv(os.path.join(DATA_DIR, "dataset_v3.csv"))

X = df[["c", "saison", "wti_lag1", "wti_lag2", "c_lag1"]].values
y = df["prix_pompe"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(f"R² train = {r2_score(y_train, model.predict(X_train)):.4f}")
print(f"R² test  = {r2_score(y_test,  model.predict(X_test)):.4f}")
print(f"MAE test = {mean_absolute_error(y_test, model.predict(X_test)):.2f} ¢/L")

features = ["c", "saison", "wti_lag1", "wti_lag2", "c_lag1"]
for f, imp in zip(features, model.feature_importances_):
    print(f"  {f}: {imp:.4f}")

output = os.path.join(MODEL_DIR, "model.pkl")
with open(output, "wb") as f:
    pickle.dump(model, f)

print(f"\nModèle sauvegardé dans {output}")
