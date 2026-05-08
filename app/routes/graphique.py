from fastapi import APIRouter, HTTPException
from datetime import date
from app.services.csv_service import get_historique, get_historique_region, get_regions

router = APIRouter()


@router.get("/graphique")
def graphique(date_debut: date):
    return {"data": get_historique(date_debut)}


@router.get("/graphique/regions")
def graphique_regions(date_debut: date, region: str):
    regions_connues = get_regions()
    if region not in regions_connues:
        raise HTTPException(status_code=404, detail=f"Région inconnue. Régions disponibles: {regions_connues}")
    return {"region": region, "data": get_historique_region(region, date_debut)}
