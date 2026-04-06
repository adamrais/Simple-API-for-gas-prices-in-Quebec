import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
import pickle

df = pd.read_csv("dataset_v3.csv")

X = df[["c", "saison"]].values
y = df["prix_pompe"].values

model = LinearRegression()
model.fit(X, y)

print(f"R²  = {r2_score(y, model.predict(X)):.4f}")
print(f"MAE = {mean_absolute_error(y, model.predict(X)):.2f} ¢/L")
print(f"a0  = {model.intercept_:.4f}")
print(f"a1  = {model.coef_[0]:.4f}  (c en CAD/L)")
print(f"a2  = {model.coef_[1]:.4f}  (saison)")

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\nModèle sauvegardé!")