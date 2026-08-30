from fastapi import APIRouter, Response
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.services.regie import get_prix_par_region
from app.services.csv_service import get_stats_regions, get_stats_quebec

_TZ = ZoneInfo("America/Montreal")
# La collecte par région tourne à 10:01 ; une minute de marge pour qu'elle
# se termine avant que le cache ne soit prolongé jusqu'au lendemain.
_HEURE_MAJ = (10, 2)


def _today():
    return datetime.now(_TZ).date()


def _max_age():
    maintenant = datetime.now(_TZ)
    prochaine = maintenant.replace(hour=_HEURE_MAJ[0], minute=_HEURE_MAJ[1], second=0, microsecond=0)
    if prochaine <= maintenant:
        prochaine += timedelta(days=1)
    return max(60, int((prochaine - maintenant).total_seconds()))


router = APIRouter()


@router.get("/regions")
def regions():
    return get_prix_par_region()


@router.get("/regions/stats")
def regions_stats(response: Response):
    response.headers["Cache-Control"] = f"public, max-age={_max_age()}"
    return {
        "date": str(_today()),
        "quebec": get_stats_quebec(),
        "regions": get_stats_regions(),
    }
