from fastapi import APIRouter
from datetime import date
from app.services.fetcher import get_wti_usdcad, get_saison
from app.services.predictor import predict_today, predict_future

router = APIRouter()


@router.get("/predict")
def predict():
    wti, wti_lag1, wti_lag2, usdcad = get_wti_usdcad()
    saison = get_saison()
    if wti is None:
        return {"erreur": "Impossible de fetch les données"}

    c      = (wti * usdcad) / 158.987
    c_lag1 = (wti_lag1 * usdcad) / 158.987
    prediction = predict_today(c, saison, wti_lag1, wti_lag2, c_lag1)

    return {
        "date": str(date.today()),
        "wti_usd": round(wti, 2),
        "usdcad": round(usdcad, 4),
        "c_cad_par_litre": round(c, 4),
        "saison": "été" if saison == 1 else "hiver",
        "prix_predit_cents": round(prediction, 2),
        "prix_predit_dollars": round(prediction / 100, 4),
    }


@router.get("/predict/futur")
def predict_futur(jours: int = 7):
    wti, wti_lag1, wti_lag2, usdcad = get_wti_usdcad()
    if wti is None:
        return {"erreur": "Impossible de fetch les données"}

    saison = get_saison()
    c      = (wti * usdcad) / 158.987
    c_lag1 = (wti_lag1 * usdcad) / 158.987
    prix_aujourdhui = predict_today(c, saison, wti_lag1, wti_lag2, c_lag1)

    return {"predictions": predict_future(prix_aujourdhui, jours)}
