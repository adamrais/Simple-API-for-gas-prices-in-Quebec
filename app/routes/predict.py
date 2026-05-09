from fastapi import APIRouter
from datetime import datetime
from zoneinfo import ZoneInfo
from app.services.regie import get_prix_regie, get_prix_par_region
from app.services.market import get_wti, get_usdcad
from app.services.csv_service import get_tendance
from app.services.predictor import predict_future, predict_future_regions

def _today():
    return datetime.now(ZoneInfo("America/Montreal")).date()

router = APIRouter()


@router.get("/predict")
def predict():
    prix = get_prix_regie()
    if prix is None:
        return {"erreur": "Impossible de fetch les données"}
    wti = get_wti()
    usdcad = get_usdcad()
    return {
        "date": str(_today()),
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


@router.get("/predict/regions")
def predict_regions(jours: int = 7):
    regions_prix = get_prix_par_region()
    if not regions_prix:
        return {"erreur": "Impossible de fetch les données"}
    return {"predictions": predict_future_regions(regions_prix, jours)}
