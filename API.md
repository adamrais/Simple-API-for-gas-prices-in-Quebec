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

Statistiques pour l'ensemble du Québec et par région administrative : prix du jour, de la veille, et moyennes sur 7 et 30 jours. Calculé à partir de l'historique enregistré (aucun appel externe — réponse en quelques millisecondes).

**Réponse :**
```json
{
  "date": "2026-08-30",
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
| `quebec` | object | Mêmes quatre champs, pour l'ensemble de la province |
| `region` | string | Nom de la région administrative |
| `aujourd_hui` | float \| null | Prix moyen enregistré aujourd'hui |
| `hier` | float \| null | Prix moyen enregistré la veille |
| `moyenne_7j` | float \| null | Moyenne sur la fenêtre des 7 derniers jours (aujourd'hui inclus) |
| `moyenne_30j` | float \| null | Moyenne sur la fenêtre des 30 derniers jours (aujourd'hui inclus) |

Le tableau `regions` est trié par nom de région. Les moyennes portent sur les jours **réellement enregistrés** dans la fenêtre.

> **Ce sont des relevés ponctuels, pas des moyennes journalières.** Le prix provincial est capté à 10 h 00 et les prix régionaux à 10 h 01 (heure de Montréal), par deux appels distincts au flux de la Régie. `moyenne_7j` et `moyenne_30j` sont donc des moyennes de ces relevés quotidiens.

> **`quebec` n'est pas la moyenne du tableau `regions`.** C'est la moyenne de toutes les stations de la province (~2 450), où les régions comptant le plus de stations pèsent davantage. La moyenne arithmétique des 18 valeurs régionales donne un résultat plus élevé — écart mesuré de 1,5 ¢ sur un instantané unique — car elle accorde le même poids à `Municipalités hors MRC \ CMM` (1 station) qu'à la Montérégie (380 stations).

> Un champ vaut `null` si aucune donnée n'existe pour la période. En pratique, `aujourd_hui` est `null` chaque matin entre minuit et la collecte quotidienne de 10 h 01 — prévoyez des types optionnels côté client.

**Cache :** la réponse porte un en-tête `Cache-Control: public, max-age=N` où `N` est le nombre de secondes restant avant la prochaine collecte (10 h 02, heure de Montréal). Les clients HTTP standards (`URLSession`, navigateurs) évitent ainsi les appels redondants.

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
