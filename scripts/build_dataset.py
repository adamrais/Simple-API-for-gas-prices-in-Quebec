import requests
import pandas as pd
import os

API_KEY = "cyhLxyvxZEPi7cDWqOMgcae7e3zofdQr5u50lZHn"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

url = (
    f"https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={API_KEY}"
    f"&frequency=weekly&data[]=value&facets[series][]=RWTC"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=1000"
)
r = requests.get(url)
data = r.json()["response"]["data"]
wti = pd.DataFrame(data)[["period", "value"]]
wti.columns = ["date", "wti"]
wti["wti"] = pd.to_numeric(wti["wti"], errors="coerce")
wti["date"] = pd.to_datetime(wti["date"])

url2 = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?recent=1000"
r2 = requests.get(url2)
obs = r2.json()["observations"]
usdcad = pd.DataFrame([{"date": o["d"], "usdcad": float(o["FXUSDCAD"]["v"])} for o in obs])
usdcad["date"] = pd.to_datetime(usdcad["date"])

pompe = pd.read_csv(os.path.join(DATA_DIR, "prix_pompe_complet.csv"))
pompe["date"] = pd.to_datetime(pompe["date"])

wti   = wti.set_index("date").resample("W-MON").mean().reset_index()
usdcad = usdcad.set_index("date").resample("W-MON").mean().reset_index()

df = pompe.merge(wti, on="date", how="inner")
df = df.merge(usdcad, on="date", how="inner")
df["c"] = (df["wti"] * df["usdcad"]) / 158.987
df = df[["date", "prix_pompe", "wti", "usdcad", "c", "saison"]].dropna()
df = df.sort_values("date").reset_index(drop=True)

print(f"Total: {len(df)} observations")
print(f"Période: {df['date'].min().date()} → {df['date'].max().date()}")
print(df.head(3))

df["wti_lag1"] = df["wti"].shift(1)
df["wti_lag2"] = df["wti"].shift(2)
df["c_lag1"]   = df["c"].shift(1)
df = df.dropna()

output = os.path.join(DATA_DIR, "dataset_v3.csv")
df.to_csv(output, index=False)
print(f"\ndataset_v3.csv sauvegardé dans {output}")
