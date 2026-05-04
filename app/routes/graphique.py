from fastapi import APIRouter
from datetime import date
from app.services.csv_service import get_historique

router = APIRouter()


@router.get("/graphique")
def graphique(date_debut: date):
    return {"data": get_historique(date_debut)}
