import csv
from datetime import date
from app.config import CSV_PATH


def load_prix():
    with open(CSV_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_prix(date_recherche: str):
    lignes = load_prix()
    return {l["date"]: float(l["prix_pompe"]) for l in lignes}.get(date_recherche)


def get_tendance():
    prix_list = [float(l["prix_pompe"]) for l in load_prix()]
    if len(prix_list) < 2:
        return "pas assez de données pour déterminer la tendance"
    derniere = prix_list[-1]
    count = 0
    i = len(prix_list) - 1
    if derniere > prix_list[-2]:
        while i > 0 and prix_list[i] > prix_list[i - 1]:
            count += 1
            i -= 1
        return f"le prix est en hausse depuis {count} jour(s)"
    elif derniere < prix_list[-2]:
        while i > 0 and prix_list[i] < prix_list[i - 1]:
            count += 1
            i -= 1
        return f"le prix est en baisse depuis {count} jour(s)"
    return "prix stable"


def get_historique(date_debut: date):
    today = date.today()
    return [l for l in load_prix() if date_debut <= date.fromisoformat(l["date"]) <= today]
