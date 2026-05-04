from fastapi import APIRouter
from datetime import date
from app.services.regie import get_prix_regie
from app.services.market import get_wti, get_usdcad
from app.services.csv_service import get_tendance
from app.services.predictor import predict_future

router = APIRouter()


@router.get("/predict")
def predict():
    prix = get_prix_regie()
    if prix is None:
        return {"erreur": "Impossible de fetch les données"}
    wti = get_wti()
    usdcad = get_usdcad()
    return {
        "date": str(date.today()),
        "wti_usd": round(wti, 2) if wti else None,
        "usdcad": round(usdcad, 4) if usdcad else None,
        "prix_predit_cents": prix,
        "prix_predit_dollars": round(prix / 100, 4),
        "tendance": get_tendance(),
    }


@router.get("/predict/futur")
def predict_futur(jours: int = 7):
    prix_aujourdhui = get_prix_regie()
    if prix_aujourdhui is None:
        return {"erreur": "Impossible de fetch les données"}
    return {"predictions": predict_future(prix_aujourdhui, jours)}
