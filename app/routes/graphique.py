from fastapi import APIRouter
from datetime import date
import csv
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, "data", "prix_quotidien.csv")
with open(CSV_PATH, encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))

today = date.today()

def get_prix_historique(date_debut: date):
    return [
        ligne for ligne in lignes
        if date_debut <= date.fromisoformat(ligne["date"]) <= today
    ]

@router.get("/graphique")
def graphique(date_debut: date):
    data = get_prix_historique(date_debut)
    return {"data": data}