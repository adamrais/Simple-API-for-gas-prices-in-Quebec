import pandas as pd
from datetime import date, timedelta
from app.config import CSV_PATH, CSV_REGIONS_PATH
from app.services.market import get_wti, get_usdcad, get_tendance_wti, get_tendance_usdcad


def _get_market_tendance():
    try:
        tendance_wti = get_tendance_wti()
        tendance_usdcad = get_tendance_usdcad()
        wti = get_wti()
        usdcad = get_usdcad()
        return (tendance_wti * usdcad + wti * tendance_usdcad) / 158.987
    except Exception:
        return 0.0


def _get_tendance_prix():
    try:
        df = pd.read_csv(CSV_PATH).sort_values("date").reset_index(drop=True)
        derniers = df["prix_pompe"].iloc[-5:].values
        tendance_historique = (derniers[-1] - derniers[0]) / len(derniers)
        tendance_marche = _get_market_tendance()
        return round(0.3 * tendance_historique + 0.7 * tendance_marche, 2)
    except Exception as e:
        print(f"Erreur tendance prix: {e}")
        return 0.0


def _get_tendance_region(region, tendance_marche):
    try:
        df = pd.read_csv(CSV_REGIONS_PATH)
        df = df[df["region"] == region].sort_values("date").reset_index(drop=True)
        if len(df) >= 5:
            derniers = df["prix"].iloc[-5:].values
        else:
            df_global = pd.read_csv(CSV_PATH).sort_values("date").reset_index(drop=True)
            derniers = df_global["prix_pompe"].iloc[-5:].values
        tendance_historique = (derniers[-1] - derniers[0]) / len(derniers)
        return round(0.3 * tendance_historique + 0.7 * tendance_marche, 2)
    except Exception as e:
        print(f"Erreur tendance région {region}: {e}")
        return round(0.7 * tendance_marche, 2)


def _build_predictions(prix_base, tendance, jours):
    resultats = []
    for j in range(1, jours + 1):
        moy = round(prix_base + tendance * j, 2)
        delta = round(1.0 + j * 0.3, 2)
        resultats.append({
            "date": str(date.today() + timedelta(days=j)),
            "optimiste": round(moy - delta, 2),
            "pessimiste": round(moy + delta, 2),
            "moyen": moy,
        })
    return resultats


def predict_future(prix_aujourdhui, jours):
    tendance = _get_tendance_prix()
    return _build_predictions(prix_aujourdhui, tendance, jours)


def predict_future_regions(regions_prix, jours):
    tendance_marche = _get_market_tendance()
    return {
        region: _build_predictions(prix, _get_tendance_region(region, tendance_marche), jours)
        for region, prix in regions_prix.items()
    }
