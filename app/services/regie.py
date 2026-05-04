import requests
import gzip
import json
from collections import defaultdict

_REGIE_URL = "https://regieessencequebec.ca/stations.geojson.gz"
_REGIE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://regieessencequebec.ca/"
}


def _fetch_stations():
    r = requests.get(_REGIE_URL, headers=_REGIE_HEADERS)
    try:
        return json.loads(gzip.decompress(r.content))
    except Exception:
        return json.loads(r.content)


def get_prix_regie():
    try:
        data = _fetch_stations()
        prix = []
        for feature in data["features"]:
            for p in feature["properties"].get("Prices", []):
                if p.get("GasType") == "Régulier" and p.get("IsAvailable"):
                    prix.append(float(p["Price"].replace("¢", "")))
        return round(sum(prix) / len(prix), 1)
    except Exception as e:
        print(f"Erreur Régie: {e}")
        return None


def get_prix_par_region():
    data = _fetch_stations()
    prix_par_region = defaultdict(list)
    for feature in data["features"]:
        props = feature["properties"]
        region = props.get("Region")
        for p in props.get("Prices", []):
            if p.get("GasType") == "Régulier" and p.get("IsAvailable"):
                try:
                    prix_par_region[region].append(float(p["Price"].replace("¢", "")))
                except Exception:
                    pass
    return {
        region: round(sum(prix) / len(prix), 1)
        for region, prix in prix_par_region.items()
        if prix
    }
