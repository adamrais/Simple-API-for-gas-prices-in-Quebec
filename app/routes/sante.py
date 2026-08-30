from fastapi import APIRouter, Response
from app.services.stations_db import get_sante

router = APIRouter()


@router.get("/sante")
def sante(response: Response):
    """Fraîcheur des données. Renvoie 503 si une source a décroché."""
    etat = get_sante()
    etat["ok"] = all(etat[k]["a_jour"] for k in ("releves", "marche", "csv"))
    response.headers["Cache-Control"] = "no-store"
    if not etat["ok"]:
        response.status_code = 503
    return etat
