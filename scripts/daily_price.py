import requests
import json
import gzip
import pandas as pd
from datetime import date
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "prix_quotidien.csv")

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

prix = get_prix_regie()
if prix:
    nouvelle_ligne = pd.DataFrame([{"date": str(date.today()), "prix_pompe": prix}])
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df = pd.concat([df, nouvelle_ligne]).drop_duplicates(subset="date").reset_index(drop=True)
    else:
        df = nouvelle_ligne
    df.to_csv(CSV_PATH, index=False)
    print(f"Prix ajouté: {prix} ¢/L ({date.today()})")
else:
    print("Erreur: prix non récupéré")