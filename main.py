import pickle
import numpy as np
from fastapi import FastAPI
from datetime import date
import requests

app = FastAPI()

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

def get_wti_usdcad():
    try:
        API_KEY = "cyhLxyvxZEPi7cDWqOMgcae7e3zofdQr5u50lZHn"
        url = f"https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={API_KEY}&frequency=weekly&data[]=value&facets[series][]=RWTC&sort[0][column]=period&sort[0][direction]=desc&length=1"
        r = requests.get(url)
        wti = float(r.json()["response"]["data"][0]["value"])

        url2 = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?recent=1"
        r2 = requests.get(url2)
        usdcad = float(r2.json()["observations"][0]["FXUSDCAD"]["v"])

        return wti, usdcad
    except Exception as e:
        print(f"Erreur fetch: {e}")
        return None, None

def get_saison():
    return 1 if date.today().month in [6, 7, 8] else 0

@app.get("/predict")
def predict():
    wti, usdcad = get_wti_usdcad()
    saison = get_saison()

    if wti is None:
        return {"erreur": "Impossible de fetch les données"}

    c = (wti * usdcad) / 158.987
    x = np.array([[c, saison]])
    prediction = model.predict(x)[0]

    return {
        "date": str(date.today()),
        "wti_usd": round(wti, 2),
        "usdcad": round(usdcad, 4),
        "c_cad_par_litre": round(c, 4),
        "saison": "été" if saison == 1 else "hiver",
        "prix_predit_cents": round(prediction, 2),
        "prix_predit_dollars": round(prediction / 100, 4)
    }

@app.get("/")
def home():
    return {"status": "ok", "message": "API Prix Pompe en ligne!"}