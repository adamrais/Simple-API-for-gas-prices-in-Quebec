from fastapi import APIRouter, HTTPException
from app.services.csv_service import get_prix

router = APIRouter()


@router.get("/prix")
def prix_par_date(date: str):
    prix = get_prix(date)
    if prix is None:
        raise HTTPException(status_code=404, detail="Date introuvable")
    return {"date": date, "prix": prix}