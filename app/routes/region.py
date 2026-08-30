from fastapi import APIRouter
from datetime import datetime
from zoneinfo import ZoneInfo
from app.services.regie import get_prix_par_region
from app.services.csv_service import get_stats_regions

def _today():
    return datetime.now(ZoneInfo("America/Montreal")).date()

router = APIRouter()


@router.get("/regions")
def regions():
    return get_prix_par_region()


@router.get("/regions/stats")
def regions_stats():
    return {"date": str(_today()), "regions": get_stats_regions()}
