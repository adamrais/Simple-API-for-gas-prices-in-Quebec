import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import date
from app.services.regie import get_prix_regie
from app.config import CSV_PATH

prix = get_prix_regie()
if prix:
    nouvelle_ligne = pd.DataFrame([{"date": str(date.today()), "prix_pompe": prix}])
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df = pd.concat([df, nouvelle_ligne]).drop_duplicates(subset="date").reset_index(drop=True)
    else:
        df = nouvelle_ligne
    df.to_csv(CSV_PATH, index=False)
    print(f"Prix ajouté: {prix} ¢/L ({date.today()})")
else:
    print("Erreur: prix non récupéré")
