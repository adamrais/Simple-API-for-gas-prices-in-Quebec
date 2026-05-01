import csv
import os 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, "data", "prix_quotidien.csv")

with open(CSV_PATH, encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))

prix_par_date = {ligne["date"]: float(ligne["prix_pompe"]) for ligne in lignes}

def get_prix(date_recherche):
    return prix_par_date.get(date_recherche)
