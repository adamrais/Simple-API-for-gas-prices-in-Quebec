import csv
import os
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, "data", "prix_quotidien.csv"), encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))

aujourd_hui = date.today()
semaine_courante = aujourd_hui.isocalendar()[1]
annee_courante = aujourd_hui.isocalendar()[0]

prix_semaine = []
for ligne in lignes:
    d = datetime.strptime(ligne['date'], "%Y-%m-%d").date()
    iso = d.isocalendar()
    if iso[0] == annee_courante and iso[1] == semaine_courante:
        prix_semaine.append(float(ligne['prix_pompe']))

moyenne = round(sum(prix_semaine) / len(prix_semaine), 1) if prix_semaine else None

rows = ""
for ligne in lignes[-7:]:
    rows += f"""
        <tr>
          <td style="padding: 8px; border: 1px solid #444;">{ligne['date']}</td>
          <td style="padding: 8px; border: 1px solid #444; color: #4caf7d;">{ligne['prix_pompe']}¢</td>
        </tr>"""

moyenne_html = ""
if moyenne is not None:
    moyenne_html = f"""
    <p style="margin-top: 20px; font-size: 16px;">
      Moyenne de la semaine : <span style="color: #4caf7d; font-weight: bold;">{moyenne}¢/L</span>
      <span style="color: #888; font-size: 13px;">({len(prix_semaine)} jour{'s' if len(prix_semaine) > 1 else ''})</span>
    </p>"""

html = f"""<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Données historiques</title>
    <style>
    body {{
        background-color: #0f0f0f;
        color: #e0e0e0;
        font-family: sans-serif;
        padding: 20px;
      }}
    #titre-principal {{
        color: #4caf7d;
        font-family: Georgia, serif;
      }}
    #nav button {{
        background-color: transparent;
        color: #4caf7d;
        border: 1px solid #4caf7d;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 15px;
        cursor: pointer;
    }}
    #nav button:hover {{
        background-color: #4caf7d;
        color: #0f0f0f;
    }}
    </style>
  </head>
  <body>
    <div id="nav">
      <a href="aujourd-hui.html"><button>Prix aujourd'hui</button></a>
    </div>
    <h1 id="titre-principal">Données historiques</h1>
    {moyenne_html}
    <table style="border-collapse: collapse; width: 100%;">
      <tr>
        <th style="padding: 8px; border: 1px solid #444;">Date</th>
        <th style="padding: 8px; border: 1px solid #444; color: #4caf7d;">Prix (¢/L)</th>
      </tr>
      {rows}
    </table>
  </body>
</html>"""

with open(os.path.join(BASE_DIR, "Site Essence", "historique.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("historique.html mis à jour !")
