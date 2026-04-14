import requests
from datetime import date
from app.config import EIA_API_KEY


def get_wti_usdcad():
    try:
        url = (
            f"https://api.eia.gov/v2/petroleum/pri/spt/data/"
            f"?api_key={EIA_API_KEY}&frequency=weekly&data[]=value"
            f"&facets[series][]=RWTC&sort[0][column]=period"
            f"&sort[0][direction]=desc&offset=0&length=3"
        )
        r = requests.get(url)
        data = r.json()["response"]["data"]
        wti_now  = float(data[0]["value"])
        wti_lag1 = float(data[1]["value"])
        wti_lag2 = float(data[2]["value"])

        url2 = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?recent=1"
        r2 = requests.get(url2)
        usdcad = float(r2.json()["observations"][0]["FXUSDCAD"]["v"])

        return wti_now, wti_lag1, wti_lag2, usdcad
    except Exception as e:
        print(f"Erreur fetch: {e}")
        return None, None, None, None


def get_saison():
    return 1 if date.today().month in [6, 7, 8] else 0
