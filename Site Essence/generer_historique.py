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
          <td style="padding: 8px; border: 4px solid #003DA5;">{ligne['date']}</td>
          <td style="padding: 8px; border: 4px solid #003DA5; color: #003DA5;">{ligne['prix_pompe']}¢</td>
        </tr>"""

moyenne_html = ""
if moyenne is not None:
    moyenne_html = f"""
    <p style="margin-top: 20px; font-size: 16px;">
      Moyenne de la semaine : <span style="color: #003DA5; font-weight: bold;">{moyenne}¢/L</span>
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
      background-color: white;  
      font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', sans-serif;
      padding: 20px;
      margin: 0;
      text-align: center;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
  }}
    main {{
      flex: 1;
    }}
    #titre-principal {{
      color: #003DA5;
      font-size: 120px;
      font-weight: bold;
      text-align: center;
      margin: 0;
      border-bottom: 4px solid #003DA5;
      padding: 10px 20px;
      display: inline-block;
  }}
    h2 {{
      margin-top: 4px;
      font-size: 18px;
      text-align: center;
      color: #003DA5;
      font-family: 'Lucida Sans', sans-serif;
  }}
    #nav {{
      text-align: center;
      margin-top: 20px;
  }}
    #nav button {{
      background-color: white;
      color: #003DA5;
      border: 2px solid #003DA5;
      border-radius: 8px;
      padding: 10px 28px;
      font-size: 20px;
      font-family: 'Lucida Sans', sans-serif;
      cursor: pointer;
      margin: 0 8px;
      margin-bottom: 20px; 
      transition: background-color 0.2s, color 0.2s;
  }}
    #nav button:hover {{
      background-color: #003DA5;
      color: white;
  }}
    #btn-chercher {{
      background-color: transparent;
      color: #003DA5;
      border: 1px solid #003DA5;
      padding: 8px 12px;
      border-radius: 4px;
      cursor: pointer;
  }}
    #btn-chercher:hover {{
      background-color: #003DA5;
      color: white;
  }}
    </style>
  </head>
  <body>
    <main>
    <h1 id="titre-principal">Données historiques</h1>
    <div id="nav">
      <a href="aujourd-hui.html"><button>Prix aujourd'hui</button></a>
      <a href="index.html"><button>Accueil</button></a>
    </div>
    <table style="border-collapse: collapse; width: 100%;">
      <tr>
        <th style="padding: 8px; border: 4px solid #003DA5; background-color: #003DA5; color: white;">Date</th>
        <th style="padding: 8px; border: 4px solid #003DA5; background-color: #003DA5; color: white;">Prix moyen au Québec(¢/L)</th>
      </tr>
      {rows}
    </table>
    {moyenne_html}
    <hr style="margin-top: 10px;">
    <h2>Chercher une date spécifique</h2>
    <input type="date" id="date-input" style="border: 1px solid #003DA5; border-radius: 4px; background-color: transparent; color: #003DA5; padding: 8px 12px; font-size: 16px;">
    <button id="btn-chercher" onclick="chercher()">Chercher</button>
    <div id="resultat" style="margin-top: 20px;"></div>

    <script>
      async function chercher() {{
        const date = document.getElementById("date-input").value;
        const res = await fetch(`http://localhost:8000/prix?date=${{date}}`);
        if (res.ok) {{
          const data = await res.json();
          document.getElementById("resultat").textContent = `Prix le ${{date}} : ${{data.prix}} ¢/L`;
        }} else {{
          document.getElementById("resultat").textContent = "Aucune donnée pour cette date.";
        }}
      }}
    </script>
    </main>
    <footer style="background-color: #003DA5; color: white; padding: 20px 40px; text-align: center;">
      <a href="index.html" style="color: white; text-decoration: none; margin: 0 15px;">Accueil</a>
      <a href="aujourd-hui.html" style="color: white; text-decoration: none; margin: 0 15px;">Prix aujourd'hui</a>
      <a href="prediction.html" style="color: white; text-decoration: none; margin: 0 15px;">Prédiction</a>
      <a href="historique.html" style="color: white; text-decoration: none; margin: 0 15px;">Données historiques</a>
      <p style="font-size: 11px; color: rgba(255,255,255,0.6); margin-top: 12px; margin-bottom: 0;">
        Conditions d'utilisation &nbsp;|&nbsp; Politique de confidentialité &nbsp;|&nbsp; Contactez-nous
      </p>
    </footer>
  </body>
</html>"""

with open(os.path.join(BASE_DIR, "Site Essence", "historique.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("historique.html mis à jour !")
