from fastapi import APIRouter, HTTPException, Query, Response
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.services.regie import get_prix_par_region
from app.services.stations_db import (
    get_stats_regions_db, get_stats_quebec_db,
    INTERVALLE_MINUTES, CARBURANTS, CARBURANT_DEFAUT,
)

_TZ = ZoneInfo("America/Montreal")


def _today():
    return datetime.now(_TZ).date()


def _max_age():
    """Expire au prochain échantillonnage : les agrégats changent toutes les
    INTERVALLE_MINUTES. Une minute de marge pour que le relevé se termine."""
    maintenant = datetime.now(_TZ)
    passees = maintenant.minute % INTERVALLE_MINUTES
    prochaine = (maintenant.replace(second=0, microsecond=0)
                 - timedelta(minutes=passees)
                 + timedelta(minutes=INTERVALLE_MINUTES + 1))
    return max(60, int((prochaine - maintenant).total_seconds()))


router = APIRouter()


@router.get("/regions")
def regions():
    return get_prix_par_region()


@router.get("/regions/stats")
def regions_stats(response: Response, carburant: str = Query(CARBURANT_DEFAUT)):
    if carburant not in CARBURANTS:
        raise HTTPException(400, detail=f"Carburant inconnu. Valeurs acceptées: {list(CARBURANTS)}")
    response.headers["Cache-Control"] = f"public, max-age={_max_age()}"
    return {
        "date": str(_today()),
        "carburant": carburant,
        "quebec": get_stats_quebec_db(carburant),
        "regions": get_stats_regions_db(carburant),
    }
