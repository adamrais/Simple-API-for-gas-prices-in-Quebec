import requests


def _fetch_yahoo(symbol, range_="1d"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range={range_}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    return r.json()


def get_wti():
    try:
        data = _fetch_yahoo("CL=F")
        return float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])
    except Exception as e:
        print(f"Erreur WTI: {e}")
        return None


def get_usdcad():
    try:
        data = _fetch_yahoo("USDCAD=X")
        return float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])
    except Exception as e:
        print(f"Erreur USDCAD: {e}")
        return None


def get_tendance_wti():
    try:
        data = _fetch_yahoo("CL=F", range_="5d")
        closes = [x for x in data["chart"]["result"][0]["indicators"]["quote"][0]["close"] if x is not None]
        return round((closes[-1] - closes[0]) / len(closes), 4)
    except Exception as e:
        print(f"Erreur tendance WTI: {e}")
        return 0.0


def get_tendance_usdcad():
    try:
        data = _fetch_yahoo("USDCAD=X", range_="5d")
        closes = [x for x in data["chart"]["result"][0]["indicators"]["quote"][0]["close"] if x is not None]
        return round((closes[-1] - closes[0]) / len(closes), 6)
    except Exception:
        return 0.0
