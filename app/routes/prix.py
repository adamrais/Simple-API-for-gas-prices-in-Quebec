from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from app.services.csv_service import get_prix
from app.config import CSV_PATH
import os

router = APIRouter()


@router.get("/prix")
def prix_par_date(date: str):
    prix = get_prix(date)
    if prix is None:
        raise HTTPException(status_code=404, detail="Date introuvable")
    return {"date": date, "prix": prix}


@router.get("/prix/csv", response_class=PlainTextResponse)
def telecharger_csv():
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="CSV introuvable")
    with open(CSV_PATH, "r") as f:
        return f.read()