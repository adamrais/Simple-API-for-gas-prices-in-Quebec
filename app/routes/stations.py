from typing import Optional

from fastapi import APIRouter, HTTPException, Response, Query
from app.services.stations_db import (
    get_stations, get_station, get_station_par_adresse, INTERVALLE_MINUTES,
)

router = APIRouter()

_CACHE_LISTE = 86400              # les métadonnées de station bougent rarement
_CACHE_STATION = INTERVALLE_MINUTES * 60


@router.get("/stations")
def stations(response: Response, region: Optional[str] = Query(None)):
    """Liste des stations, sans prix — pour découvrir les identifiants."""
    response.headers["Cache-Control"] = f"public, max-age={_CACHE_LISTE}"
    liste = get_stations()
    if region:
        liste = [s for s in liste if s["region"] == region]
        if not liste:
            regions = sorted({s["region"] for s in get_stations() if s["region"]})
            raise HTTPException(404, detail=f"Région inconnue. Régions disponibles: {regions}")
    return {"stations": liste}


@router.get("/stations/stats")
def station_par_adresse(adresse: str, response: Response):
    """Mêmes statistiques, retrouvées par l'adresse exacte du flux de la Régie."""
    s = get_station_par_adresse(adresse)
    if s is None:
        raise HTTPException(404, detail="Adresse introuvable")
    response.headers["Cache-Control"] = f"public, max-age={_CACHE_STATION}"
    return s


@router.get("/stations/{station_id}")
def station(station_id: int, response: Response):
    """Prix du jour, moyenne de la veille, moyennes 7 et 30 jours, et historique."""
    s = get_station(station_id)
    if s is None:
        raise HTTPException(404, detail="Station introuvable")
    response.headers["Cache-Control"] = f"public, max-age={_CACHE_STATION}"
    return s
