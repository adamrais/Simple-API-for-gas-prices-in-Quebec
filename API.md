# API ProEssence — Endpoints

Base URL: `https://proessence.up.railway.app`

Tous les prix sont en **¢/L** (cents par litre).

---

## GET `/predict`

Prix moyen actuel au Québec avec données de marché et tendance.

**Réponse :**
```json
{
  "date": "2026-05-08",
  "wti_usd": 58.12,
  "usdcad": 1.3821,
  "prix_predit_cents": 190.6,
  "prix_predit_dollars": 1.9060,
  "tendance": "le prix est en hausse depuis 3 jour(s)"
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `date` | string | Date du jour (`YYYY-MM-DD`) |
| `wti_usd` | float | Prix du baril WTI en USD |
| `usdcad` | float | Taux de change USD/CAD |
| `prix_predit_cents` | float | Prix moyen en ¢/L |
| `prix_predit_dollars` | float | Prix moyen en $/L |
| `tendance` | string | Tendance des derniers jours |

> Appelle des APIs externes — prévoir 2–5 secondes de délai.

---

## GET `/predict/futur`

Prédiction des prix pour les prochains jours (fourchette optimiste / moyen / pessimiste).

**Paramètres :**

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `jours` | int | `7` | Nombre de jours à prédire (ex: `?jours=14`) |

**Réponse :**
```json
{
  "predictions": [
    { "date": "2026-05-09", "optimiste": 188.9, "moyen": 190.2, "pessimiste": 191.5 },
    { "date": "2026-05-10", "optimiste": 187.6, "moyen": 190.4, "pessimiste": 193.2 }
  ]
}
```

---

## GET `/predict/regions`

Prédiction des prix pour les prochains jours, par région administrative du Québec.

**Paramètres :**

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `jours` | int | `7` | Nombre de jours à prédire (ex: `?jours=14`) |

**Réponse :**
```json
{
  "predictions": {
    "Montréal": [
      { "date": "2026-05-09", "optimiste": 187.5, "moyen": 189.1, "pessimiste": 190.7 }
    ],
    "Québec": [
      { "date": "2026-05-09", "optimiste": 189.2, "moyen": 190.8, "pessimiste": 192.4 }
    ]
  }
}
```

> Appelle des APIs externes — prévoir 2–5 secondes de délai.

---

## GET `/regions`

Prix moyen actuel par région administrative du Québec (données temps réel de la Régie de l'énergie).

**Réponse :**
```json
{
  "Montréal": 189.4,
  "Québec": 191.2,
  "Laval": 188.7,
  "Laurentides": 192.0
}
```

> Appelle des APIs externes — prévoir 2–5 secondes de délai.

---

## GET `/regions/stats`

Statistiques pour l'ensemble du Québec et par région administrative : prix du jour, de la veille, et moyennes sur 7 et 30 jours. Agrégé depuis les relevés station effectués toutes les 30 minutes (base SQLite, aucun appel externe).

**Carburant :** ajoutez `?carburant=Super` ou `?carburant=Diesel` pour changer de carburant. Valeurs acceptées : `Régulier` (défaut), `Super`, `Diesel` — toute autre valeur renvoie `400`. Le diesel n'est vendu que par ~2 000 des ~2 450 stations ; une station qui ne le vend pas renvoie `null` et un historique vide.


**Réponse :**
```json
{
  "date": "2026-08-30",
  "carburant": "Régulier",
  "quebec": {
    "aujourd_hui": 185.2,
    "hier": 184.4,
    "moyenne_7j": 183.4,
    "moyenne_30j": 181.3
  },
  "regions": [
    {
      "region": "Abitibi-Témiscamingue",
      "aujourd_hui": 187.0,
      "hier": 186.7,
      "moyenne_7j": 185.6,
      "moyenne_30j": 184.0
    },
    {
      "region": "Bas-Saint-Laurent",
      "aujourd_hui": 184.2,
      "hier": 184.3,
      "moyenne_7j": 184.0,
      "moyenne_30j": 184.3
    }
  ]
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `date` | string | Date du jour (`YYYY-MM-DD`), fuseau America/Montreal |
| `carburant` | string | Carburant demandé (`Régulier`, `Super` ou `Diesel`) |
| `quebec` | object | Mêmes quatre champs, pour l'ensemble de la province |
| `region` | string | Nom de la région administrative |
| `aujourd_hui` | float \| null | Prix moyen enregistré aujourd'hui |
| `hier` | float \| null | Prix moyen enregistré la veille |
| `moyenne_7j` | float \| null | Moyenne sur la fenêtre des 7 derniers jours (aujourd'hui inclus) |
| `moyenne_30j` | float \| null | Moyenne sur la fenêtre des 30 derniers jours (aujourd'hui inclus) |

Le tableau `regions` est trié par nom de région. Les moyennes portent sur les jours **réellement enregistrés** dans la fenêtre.

> **Ce sont de vraies moyennes journalières.** Les ~2 450 stations sont relevées toutes les 30 minutes (48 fois par jour). `aujourd_hui` est la moyenne des relevés depuis minuit — elle se précise au fil de la journée. `hier` est la moyenne complète de la veille. `moyenne_7j` et `moyenne_30j` sont les moyennes de ces moyennes quotidiennes : chaque jour compte à parts égales, quel que soit son nombre de relevés.

> **Démarrage à froid.** Cette source a été mise en service le 30 août 2026 et se remplit progressivement : `hier` apparaît après un jour, `moyenne_7j` devient significative après une semaine, `moyenne_30j` après un mois. Sur une fenêtre incomplète, la moyenne porte sur les jours réellement disponibles.

> **`quebec` n'est pas la moyenne du tableau `regions`.** C'est la moyenne de toutes les stations de la province (~2 450), où les régions comptant le plus de stations pèsent davantage. La moyenne arithmétique des 18 valeurs régionales donne un résultat plus élevé — écart mesuré de 1,5 ¢ sur un relevé unique — car elle accorde le même poids à `Municipalités hors MRC \ CMM` (1 station) qu'à la Montérégie (380 stations).

> Un champ vaut `null` si aucune donnée n'existe pour la période. En pratique, `aujourd_hui` est `null` chaque nuit entre minuit et le premier relevé (au plus 30 minutes) — prévoyez des types optionnels côté client.

**Cache :** la réponse porte un en-tête `Cache-Control: public, max-age=N` où `N` est le nombre de secondes restant avant le prochain relevé — au plus 31 minutes. Les clients HTTP standards (`URLSession`, navigateurs) évitent ainsi les appels redondants.

---

## GET `/stations`

Liste des stations, **sans prix** — sert à découvrir les identifiants à passer à `/stations/{id}`.

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| `region` | string | Filtre optionnel (ex: `?region=Montréal`) |
| `stats` | bool | `true` ajoute les 4 statistiques pour les trois carburants |

**Réponse :**
```json
{
  "stations": [
    {
      "id": 63,
      "nom": "MIGIZY ODENAW INC",
      "marque": "Crevier",
      "adresse": "1 Ogima, Kipawa",
      "region": "Abitibi-Témiscamingue",
      "lat": 46.786974,
      "lon": -78.981912
    }
  ]
}
```

> La liste complète pèse ~409 Ko (~82 Ko compressés). Utilisez `?region=` pour la réduire — Montréal ne fait que 36 Ko. Mise en cache 24 h, les métadonnées de station changent rarement.

### Avec `?stats=true`

Ajoute un objet `carburants` à chaque station — les quatre statistiques pour l'ordinaire, le super et le diesel, en une seule requête :

```json
{
  "stations": [
    {
      "id": 63,
      "nom": "MIGIZY ODENAW INC",
      "adresse": "1 Ogima, Kipawa",
      "region": "Abitibi-Témiscamingue",
      "lat": 46.786974,
      "lon": -78.981912,
      "carburants": {
        "Régulier": { "aujourd_hui": 186.9, "hier": 186.4, "moyenne_7j": 185.1, "moyenne_30j": 183.8 },
        "Super":    { "aujourd_hui": 213.9, "hier": 213.5, "moyenne_7j": 212.0, "moyenne_30j": 210.4 },
        "Diesel":   { "aujourd_hui": null,  "hier": null,  "moyenne_7j": null,  "moyenne_30j": null }
      }
    }
  ]
}
```

Les 2 465 stations pèsent ~1,06 Mo brut, **~111 Ko compressés**, servis en ~60 ms. Combinez avec `?region=` pour n'en obtenir qu'une partie (Montréal : ~9 Ko compressés). Mise en cache pour la durée de l'intervalle d'échantillonnage.

Une station qui ne vend pas un carburant renvoie ses quatre champs à `null` — c'est le cas de ~460 stations pour le diesel.

---

## GET `/stations/stats`

Identique à `/stations/{id}`, mais retrouve la station par son **adresse** — la clé fournie par le flux de la Régie. Utile si votre client récupère déjà les stations directement depuis la Régie et n'a pas les identifiants de cette API.

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| `adresse` | string | Adresse exacte, telle qu'écrite dans le flux (ex: `?adresse=1 Ogima, Kipawa`) |
| `carburant` | string | `Régulier` (défaut), `Super` ou `Diesel` |

L'adresse doit correspondre au caractère près. Retourne `404` si elle est inconnue — ce qui arrive normalement pour une station apparue dans le flux depuis le dernier relevé : prévoyez d'afficher « pas encore d'historique » plutôt qu'une erreur.

---

## GET `/stations/{id}`

Prix du jour, moyenne de la veille, moyennes 7 et 30 jours, et historique quotidien complet pour une station.

**Carburant :** ajoutez `?carburant=Super` ou `?carburant=Diesel` pour changer de carburant. Valeurs acceptées : `Régulier` (défaut), `Super`, `Diesel` — toute autre valeur renvoie `400`. Le diesel n'est vendu que par ~2 000 des ~2 450 stations ; une station qui ne le vend pas renvoie `null` et un historique vide.


**Réponse :**
```json
{
  "id": 63,
  "nom": "MIGIZY ODENAW INC",
  "marque": "Crevier",
  "adresse": "1 Ogima, Kipawa",
  "region": "Abitibi-Témiscamingue",
  "lat": 46.786974,
  "lon": -78.981912,
  "carburant": "Régulier",
  "aujourd_hui": 186.9,
  "hier": 185.4,
  "moyenne_7j": 184.2,
  "moyenne_30j": 182.0,
  "historique": [
    { "date": "2026-08-29", "moyenne": 185.4, "min": 184.9, "max": 186.9, "dernier": 185.9, "releves": 48 }
  ]
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `aujourd_hui` | float \| null | **Dernier relevé** du jour (pas une moyenne) |
| `hier` | float \| null | **Moyenne** de tous les relevés de la veille |
| `moyenne_7j` | float \| null | Moyenne pondérée sur 7 jours (pondérée par le nombre de relevés) |
| `moyenne_30j` | float \| null | Moyenne pondérée sur 30 jours |
| `historique` | array | Un objet par jour conservé, du plus ancien au plus récent |
| `historique[].releves` | int | Nombre d'échantillons ce jour-là |

**Rétention : 31 jours.** Les jours plus anciens sont supprimés chaque nuit à 3 h 30. C'est exactement ce qu'il faut pour que `moyenne_30j` reste calculable.

**Démarrage à froid :** `hier`, `moyenne_7j` et `moyenne_30j` se remplissent progressivement — il faut 30 jours de collecte avant que `moyenne_30j` soit pleine. `null` tant qu'aucune donnée n'existe.

Retourne `404` si l'identifiant est inconnu. Mise en cache pour la durée de l'intervalle d'échantillonnage.

---

## GET `/prix`

Prix moyen historique enregistré pour une date précise.

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| `date` | string | Date au format `YYYY-MM-DD` (ex: `?date=2026-05-04`) |

**Réponse :**
```json
{ "date": "2026-05-04", "prix": 190.6 }
```

Retourne `404` si la date est introuvable.

---

## GET `/prix/csv`

Contenu complet du fichier CSV historique des prix Québec (texte brut).

**Réponse :**
```
date,prix_pompe
2026-04-21,179.3
2026-04-22,180.4
2026-04-23,187.1
```

---

## GET `/prix/csv/regions`

Contenu complet du fichier CSV historique des prix par région (texte brut).

**Réponse :**
```
date,region,prix
2026-05-08,Montréal,189.4
2026-05-08,Québec,191.2
2026-05-08,Laval,188.7
```

---

## GET `/graphique`

Données historiques des prix Québec depuis une date de début jusqu'à aujourd'hui.

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| `date_debut` | string | Date de début au format `YYYY-MM-DD` (ex: `?date_debut=2026-04-01`) |

**Réponse :**
```json
{
  "data": [
    { "date": "2026-04-21", "prix_pompe": "179.3" },
    { "date": "2026-04-22", "prix_pompe": "180.4" }
  ]
}
```

---

## GET `/graphique/regions`

Données historiques des prix pour une région spécifique depuis une date de début jusqu'à aujourd'hui.

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| `region` | string | Nom exact de la région (ex: `?region=Montréal`) |
| `date_debut` | string | Date de début au format `YYYY-MM-DD` (ex: `&date_debut=2026-04-01`) |

**Réponse :**
```json
{
  "region": "Montréal",
  "data": [
    { "date": "2026-05-01", "prix": 190.6 },
    { "date": "2026-05-02", "prix": 190.5 }
  ]
}
```

Retourne `404` si la région est inconnue, avec la liste des régions disponibles dans le message d'erreur.

---

## Notes

- Documentation interactive Swagger : `https://proessence.up.railway.app/docs`
- Les endpoints `/predict`, `/predict/futur`, `/predict/regions` et `/regions` appellent des APIs externes (Régie de l'énergie, Yahoo Finance) — prévoir 2–5 secondes de délai
- Les données régionales (`/graphique/regions`, `/prix/csv/regions`) sont disponibles à partir du 2026-05-08
