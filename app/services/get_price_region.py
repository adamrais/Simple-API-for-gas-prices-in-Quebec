import requests
import gzip
import json
from collections import defaultdict

def get_prix_par_region():
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

    prix_par_region = defaultdict(list)

    for feature in data["features"]:
        props = feature["properties"]
        region = props.get("Region")
        prices = props.get("Prices", [])
        for p in prices:
            if p.get("GasType") == "Régulier" and p.get("IsAvailable"):
                prix_str = p["Price"].replace("¢", "")
                try:
                    prix_par_region[region].append(float(prix_str))
                except:
                    pass

    return {
        region: round(sum(prix) / len(prix), 1)
        for region, prix in prix_par_region.items()
        if prix
    }