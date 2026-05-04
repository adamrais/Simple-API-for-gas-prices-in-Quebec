import pandas as pd
from datetime import date, timedelta
from app.config import CSV_PATH
from app.services.market import get_wti, get_usdcad, get_tendance_wti, get_tendance_usdcad


def _get_tendance_prix():
    try:
        df = pd.read_csv(CSV_PATH).sort_values("date").reset_index(drop=True)
        derniers = df["prix_pompe"].iloc[-5:].values
        tendance_historique = (derniers[-1] - derniers[0]) / len(derniers)

        tendance_wti = get_tendance_wti()
        tendance_usdcad = get_tendance_usdcad()
        wti = get_wti()
        usdcad = get_usdcad()
        tendance_marche = (tendance_wti * usdcad + wti * tendance_usdcad) / 158.987

        return round(0.3 * tendance_historique + 0.7 * tendance_marche, 2)
    except Exception as e:
        print(f"Erreur tendance prix: {e}")
        return 0.0


def predict_future(prix_aujourdhui, jours):
    tendance = _get_tendance_prix()
    resultats = []
    for j in range(1, jours + 1):
        moy = round(prix_aujourdhui + tendance * j, 2)
        delta = round(1.0 + j * 0.3, 2)
        resultats.append({
            "date": str(date.today() + timedelta(days=j)),
            "optimiste": round(moy - delta, 2),
            "pessimiste": round(moy + delta, 2),
            "moyen": moy,
        })
    return resultats
