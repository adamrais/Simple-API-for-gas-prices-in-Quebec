import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import date
from app.services.regie import get_prix_regie, get_prix_par_region
from app.config import CSV_PATH, CSV_REGIONS_PATH

today = str(date.today())

prix = get_prix_regie()
if prix:
    nouvelle_ligne = pd.DataFrame([{"date": today, "prix_pompe": prix}])
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df = pd.concat([df, nouvelle_ligne]).drop_duplicates(subset="date").reset_index(drop=True)
    else:
        df = nouvelle_ligne
    df.to_csv(CSV_PATH, index=False)
    print(f"Prix ajouté: {prix} ¢/L ({today})")
else:
    print("Erreur: prix non récupéré")

regions = get_prix_par_region()
if regions:
    nouvelles_lignes = pd.DataFrame([
        {"date": today, "region": region, "prix": p}
        for region, p in regions.items()
    ])
    if os.path.exists(CSV_REGIONS_PATH):
        df_r = pd.read_csv(CSV_REGIONS_PATH)
        df_r = pd.concat([df_r, nouvelles_lignes]).drop_duplicates(subset=["date", "region"]).reset_index(drop=True)
    else:
        df_r = nouvelles_lignes
    df_r.to_csv(CSV_REGIONS_PATH, index=False)
    print(f"Prix régions ajoutés: {len(regions)} régions ({today})")
else:
    print("Erreur: prix régions non récupérés")
