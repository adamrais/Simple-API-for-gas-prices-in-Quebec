# ProEssence — Quebec Gas Price API

A REST API that provides real-time and historical regular gasoline prices across Quebec, powered by live data from the Régie de l'énergie du Québec and oil market feeds.

**Live:** [proessence.up.railway.app](https://proessence.up.railway.app)  
**Interactive docs:** [proessence.up.railway.app/docs](https://proessence.up.railway.app/docs)

---

## Features

- **Live price** — current average price at the pump across Quebec
- **Three fuel grades** — regular, super and diesel, sampled every 30 minutes across ~2,450 stations
- **Regional breakdown** — average price per administrative region
- **Historical data** — daily average prices going back months
- **Price prediction** — short-term forecast for today and the next N days (optimistic / average / pessimistic bands), extrapolated from recent pump trend blended with WTI crude and USD/CAD movement

---

## Endpoints

All prices are in **¢/L** (cents per litre).

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/predict` | Today's predicted price + market data + trend |
| `GET` | `/predict/futur?jours=7` | Multi-day forecast |
| `GET` | `/prix?date=YYYY-MM-DD` | Historical price for a specific date |
| `GET` | `/regions` | Live price by Quebec administrative region |
| `GET` | `/regions/stats` | Province-wide and per-region price today, yesterday, 7-day and 30-day averages (`?carburant=Régulier\|Super\|Diesel`) |
| `GET` | `/stations` | Station directory (id, name, brand, address, region, coordinates); `?stats=true` adds all three fuels' stats |
| `GET` | `/stations/{station_id}` | Per-station stats for all three fuels (or one via `?carburant=`), plus 31-day history |
| `GET` | `/stations/stats?adresse=` | Same, looked up by the station address used in the Régie feed |
| `GET` | `/graphique?date_debut=YYYY-MM-DD` | Historical data since a start date |

### `/predict`
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

### `/predict/futur?jours=7`
```json
{
  "predictions": [
    { "date": "2026-05-05", "optimiste": 188.9, "moyen": 190.2, "pessimiste": 191.5 },
    { "date": "2026-05-06", "optimiste": 187.6, "moyen": 190.4, "pessimiste": 193.2 }
  ]
}
```

### `/regions`
```json
{
  "Montréal": 189.4,
  "Québec": 191.2,
  "Laval": 188.7,
  "Laurentides": 192.0
}
```

---

## Tech Stack

- **FastAPI** — web framework
- **scikit-learn** — price prediction model
- **pandas / numpy** — data processing
- **yfinance** — WTI crude oil and USD/CAD market data
- **Railway** — deployment

---

## Data Sources

- [Régie de l'énergie du Québec](https://regieessencequebec.ca/) — live station prices (GeoJSON feed)
- Yahoo Finance via `yfinance` — WTI crude (CL=F) and USD/CAD (CAD=X)

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python run.py
```

The API will be available at `http://localhost:8000`.

> **Note:** `/predict` and `/regions` call external APIs and may take 2–5 seconds to respond.

---

## Project Structure

```
app/
  routes/         # FastAPI route handlers
  services/
    regie.py      # Régie de l'énergie data fetching
    market.py     # WTI and USD/CAD market feeds
    predictor.py  # Price trend and forecast logic
    csv_service.py
data/
  prix_quotidien.csv   # Historical daily prices
models/
  model.pkl            # Trained ML model
scripts/
  daily_price.py       # Script to update daily price data
templates/             # Web UI
```
