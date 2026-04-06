import requests
import pandas as pd
from io import StringIO

API_KEY = "cyhLxyvxZEPi7cDWqOMgcae7e3zofdQr5u50lZHn"

url = f"https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={API_KEY}&frequency=weekly&data[]=value&facets[series][]=RWTC&sort[0][column]=period&sort[0][direction]=desc&length=300"
r = requests.get(url)
data = r.json()["response"]["data"]
wti = pd.DataFrame(data)[["period", "value"]]
wti.columns = ["date", "wti"]
wti["date"] = pd.to_datetime(wti["date"])
print("WTI OK:", len(wti), "observations")
print(wti.head(3))

url2 = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?recent=300"
r2 = requests.get(url2)
obs = r2.json()["observations"]
usdcad = pd.DataFrame([{"date": o["d"], "usdcad": float(o["FXUSDCAD"]["v"])} for o in obs])
usdcad["date"] = pd.to_datetime(usdcad["date"])
print("\nUSD/CAD OK:", len(usdcad), "observations")
print(usdcad.head(3))