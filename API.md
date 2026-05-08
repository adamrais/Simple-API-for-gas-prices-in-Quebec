# API ProEssence — Endpoints

Base URL: `https://proessence.up.railway.app`

---

## GET `/predict`

Prix moyen actuel au Québec avec données de marché et tendance.

```json
{
  "date": "2026-05-04",
  "wti_usd": 58.12,
  "usdcad": 1.3821,
  "prix_predit_cents": 190.6,
  "prix_predit_dollars": 1.9060,
  "tendance": "le prix est en baisse depuis 2 jour(s)"
}
```

---

## GET `/predict/futur?jours=7`

Prédiction des prix pour les prochains jours.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `jours`   | int  | `7`    | Nombre de jours à prédire |

```json
{
  "predictions": [
    { "date": "2026-05-05", "optimiste": 188.9, "moyen": 190.2, "pessimiste": 191.5 },
    { "date": "2026-05-06", "optimiste": 187.6, "moyen": 190.4, "pessimiste": 193.2 }
  ]
}
```

---

## GET `/prix?date=YYYY-MM-DD`

Prix moyen historique pour une date précise.

| Paramètre | Type   | Description |
|-----------|--------|-------------|
| `date`    | string | Date au format `YYYY-MM-DD` |

```json
{ "date": "2026-05-04", "prix": 190.6 }
```

Retourne `404` si la date est introuvable.

---

## GET `/prix/csv`

Contenu complet du fichier CSV historique (format texte brut).

```
date,prix_pompe
2026-04-21,179.3
2026-04-22,180.4
...
```

---

## GET `/regions`

Prix moyen actuel par région administrative du Québec.

```json
{
  "Montréal": 189.4,
  "Québec": 191.2,
  "Laval": 188.7,
  "Laurentides": 192.0
}
```

---

## GET `/graphique?date_debut=YYYY-MM-DD`

Données historiques depuis une date de début jusqu'à aujourd'hui.

| Paramètre    | Type | Description |
|--------------|------|-------------|
| `date_debut` | date | Date de début au format `YYYY-MM-DD` |

```json
{
  "data": [
    { "date": "2026-04-28", "prix_pompe": "184.2" },
    { "date": "2026-04-29", "prix_pompe": "185.7" }
  ]
}
```

---

## Notes

- Tous les prix sont en **¢/L** (cents par litre)
- `/predict` et `/regions` appellent des APIs externes — prévoir un délai de 2-5 secondes
- Documentation interactive : `https://proessence.up.railway.app/docs`
