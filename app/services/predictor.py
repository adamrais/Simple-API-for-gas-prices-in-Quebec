import pandas as pd
import requests
import os
from datetime import date, timedelta

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

def get_tendance_wti():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=1d&range=5d"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        closes = r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        closes = [x for x in closes if x is not None]
        tendance = (closes[-1] - closes[0]) / len(closes)
        return round(tendance, 4)
    except Exception as e:
        print(f"Erreur tendance WTI: {e}")
        return 0.0

def get_tendance_usdcad():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/USDCAD=X?interval=1d&range=5d"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        closes = r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        closes = [x for x in closes if x is not None]
        tendance = (closes[-1] - closes[0]) / len(closes)
        return round(tendance, 6)
    except:
        return 0.0

def get_tendance_prix():
    try:
        CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "prix_quotidien.csv")
        df = pd.read_csv(CSV_PATH)
        print(f"CSV chargé: {len(df)} lignes, dernières valeurs: {df['prix_pompe'].iloc[-5:].values}") 
        df = df.sort_values("date").reset_index(drop=True)
        derniers = df["prix_pompe"].iloc[-5:].values
        tendance_historique = (derniers[-1] - derniers[0]) / len(derniers)

        tendance_wti = get_tendance_wti()
        tendance_usdcad = get_tendance_usdcad()
        wti = get_wti_realtime()
        usdcad = get_usdcad_realtime()
        tendance_marche = (tendance_wti * usdcad + wti * tendance_usdcad) / 158.987

        tendance_finale = 0.3 * tendance_historique + 0.7 * tendance_marche
        print(f"Tendance historique: {tendance_historique}, marché: {tendance_marche}, finale: {tendance_finale}")
        return round(tendance_finale, 2)
    except Exception as e:
        print(f"Erreur tendance prix: {e}")
        return 0.0
    
def predict_future(prix_aujourdhui, jours):
    resultats = []
    tendance_essence = get_tendance_prix()
    
    for j in range(1, jours + 1):
        moy = round(prix_aujourdhui + (tendance_essence * j), 2)
        
        delta = round(1.0 + (j * 0.3), 2)
        
        resultats.append({
            "date": str(date.today() + timedelta(days=j)),
            "optimiste": round(moy - delta, 2),
            "pessimiste": round(moy + delta, 2),
            "moyen": moy,
        })
    
    return resultats