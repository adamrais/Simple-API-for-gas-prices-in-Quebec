from fastapi import APIRouter
from datetime import date
import requests
import gzip
import json
import csv
import os
from app.services.predictor import predict_future

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, "data", "prix_quotidien.csv")
with open(CSV_PATH, encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))

def get_wti_realtime():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=1d&range=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        data = r.json()
        prix = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        return float(prix)
    except Exception as e:
        print(f"Erreur WTI realtime: {e}")
        return None
def get_usdcad_realtime():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/USDCAD=X?interval=1d&range=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        data = r.json()
        prix = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        return float(prix)
    except Exception as e:
        print(f"Erreur USDCAD realtime: {e}")
        return None

def get_prix_regie():
    try:
        url = "https://regieessencequebec.ca/stations.geojson.gz"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://regieessencequebec.ca/"
        }
        r = requests.get(url, headers=headers)
        try:
            data = json.loads(gzip.decompress(r.content))
        except:
            data = json.loads(r.content)
        prix = []
        for feature in data["features"]:
            prices = feature["properties"].get("Prices", [])
            for p in prices:
                if p.get("GasType") == "Régulier" and p.get("IsAvailable"):
                    prix_str = p["Price"].replace("¢", "")
                    prix.append(float(prix_str))
        return round(sum(prix) / len(prix), 1)
    except Exception as e:
        print(f"Erreur Régie: {e}")
        return None

def get_tendance():
    with open(CSV_PATH, encoding="utf-8") as f:
        lignes_fresh = list(csv.DictReader(f))
    
    prix_list = [float(l["prix_pompe"]) for l in lignes_fresh]

    if len(prix_list) < 2:
        tendance = "pas assez de données pour déterminer la tendance"

    derniere = prix_list[-1]
    count = 0
    i = len(prix_list) - 1

    if derniere > prix_list[-2]:
        while i > 0 and prix_list[i] > prix_list[i-1]:
            count += 1
            i -= 1
        tendance = f"le prix est en hausse depuis {count} jour(s)"
    
    elif derniere < prix_list[-2]:
        while i > 0 and prix_list[i] < prix_list[i-1]:
            count += 1
            i -= 1
        tendance =  f"le prix est en baisse depuis {count} jour(s)"
    
    return tendance

@router.get("/predict")
def predict():
    prix = get_prix_regie()
    wti = get_wti_realtime()
    usdcad = get_usdcad_realtime()
    tendance = get_tendance()
    if prix is None:
        return {"erreur": "Impossible de fetch les données"}
    
    return {
        "date": str(date.today()),
        "wti_usd": round(wti, 2) if wti else None,
        "usdcad": round(usdcad, 4) if usdcad else None,
        "prix_predit_cents": prix,
        "prix_predit_dollars": round(prix / 100, 4),
        "tendance": tendance
    }

@router.get("/predict/futur")
def predict_futur(jours: int = 7):
    prix_aujourdhui = get_prix_regie()
    if prix_aujourdhui is None:
        return {"erreur": "Impossible de fetch les données"}
    
    return {"predictions": predict_future(prix_aujourdhui, jours)}