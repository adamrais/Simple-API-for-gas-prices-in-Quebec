import os
import sqlite3
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.config import STATIONS_DB_PATH
from app.services.regie import _fetch_stations

RETENTION_JOURS = 31
INTERVALLE_MINUTES = 30

_SCHEMA = """
CREATE TABLE IF NOT EXISTS stations (
    id      INTEGER PRIMARY KEY,
    adresse TEXT UNIQUE NOT NULL,
    nom     TEXT,
    marque  TEXT,
    region  TEXT,
    lat     REAL,
    lon     REAL
);

CREATE TABLE IF NOT EXISTS prix_jour (
    station_id INTEGER NOT NULL REFERENCES stations(id),
    date       TEXT NOT NULL,
    somme      REAL NOT NULL,
    n          INTEGER NOT NULL,
    prix_min   REAL NOT NULL,
    prix_max   REAL NOT NULL,
    dernier    REAL NOT NULL,
    PRIMARY KEY (station_id, date)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS idx_prix_jour_date ON prix_jour(date);
CREATE INDEX IF NOT EXISTS idx_stations_region ON stations(region);
"""


def _today():
    return datetime.now(ZoneInfo("America/Montreal")).date()


def _connect():
    os.makedirs(os.path.dirname(STATIONS_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(STATIONS_DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with _connect() as conn:
        conn.executescript(_SCHEMA)


def _prix_reguliers(data):
    for f in data["features"]:
        props = f["properties"]
        adresse = props.get("Address")
        if not adresse:
            continue
        for p in props.get("Prices", []):
            if p.get("GasType") == "Régulier" and p.get("IsAvailable"):
                try:
                    prix = float(p["Price"].replace("¢", ""))
                except (KeyError, ValueError):
                    break
                coords = (f.get("geometry") or {}).get("coordinates") or [None, None]
                yield {
                    "adresse": adresse,
                    "nom": props.get("Name"),
                    "marque": props.get("brand"),
                    "region": props.get("Region"),
                    "lon": coords[0],
                    "lat": coords[1],
                    "prix": prix,
                }
                break


def enregistrer_releve(data=None):
    """Échantillonne le flux et met à jour l'agrégat du jour. Retourne le nombre de stations."""
    if data is None:
        data = _fetch_stations()
    releves = list(_prix_reguliers(data))
    if not releves:
        return 0

    jour = str(_today())
    with _connect() as conn:
        conn.executemany(
            """INSERT INTO stations (adresse, nom, marque, region, lat, lon)
               VALUES (:adresse, :nom, :marque, :region, :lat, :lon)
               ON CONFLICT(adresse) DO UPDATE SET
                 nom=excluded.nom, marque=excluded.marque,
                 region=excluded.region, lat=excluded.lat, lon=excluded.lon""",
            releves,
        )
        ids = {a: i for i, a in conn.execute("SELECT id, adresse FROM stations")}
        conn.executemany(
            """INSERT INTO prix_jour (station_id, date, somme, n, prix_min, prix_max, dernier)
               VALUES (?, ?, ?, 1, ?, ?, ?)
               ON CONFLICT(station_id, date) DO UPDATE SET
                 somme    = somme + excluded.somme,
                 n        = n + 1,
                 prix_min = MIN(prix_min, excluded.prix_min),
                 prix_max = MAX(prix_max, excluded.prix_max),
                 dernier  = excluded.dernier""",
            [(ids[r["adresse"]], jour, r["prix"], r["prix"], r["prix"], r["prix"]) for r in releves],
        )
    return len(releves)


def elaguer(jours=RETENTION_JOURS):
    """Supprime les jours au-delà de la fenêtre de rétention. Retourne le nombre de lignes supprimées."""
    limite = str(_today() - timedelta(days=jours - 1))
    with _connect() as conn:
        n = conn.execute("DELETE FROM prix_jour WHERE date < ?", (limite,)).rowcount
    return n


def _moyenne(conn, station_id, jours, today):
    debut = str(today - timedelta(days=jours - 1))
    r = conn.execute(
        "SELECT SUM(somme) s, SUM(n) n FROM prix_jour WHERE station_id=? AND date>=?",
        (station_id, debut),
    ).fetchone()
    return round(r["s"] / r["n"], 1) if r and r["n"] else None


def get_stations():
    """Liste des stations, sans prix — pour découvrir les identifiants."""
    with _connect() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT id, nom, marque, adresse, region, lat, lon FROM stations ORDER BY region, adresse")]


def get_station(station_id):
    """Les 4 statistiques d'une station, plus son historique quotidien."""
    with _connect() as conn:
        st = conn.execute(
            "SELECT id, nom, marque, adresse, region, lat, lon FROM stations WHERE id=?",
            (station_id,),
        ).fetchone()
        if st is None:
            return None

        today = _today()
        hier = str(today - timedelta(days=1))
        lignes = conn.execute(
            """SELECT date, somme, n, prix_min, prix_max, dernier
               FROM prix_jour WHERE station_id=? ORDER BY date""",
            (station_id,),
        ).fetchall()

        par_date = {l["date"]: l for l in lignes}
        aujourdhui = par_date.get(str(today))
        veille = par_date.get(hier)

        return {
            **dict(st),
            "aujourd_hui": aujourdhui["dernier"] if aujourdhui else None,
            "hier": round(veille["somme"] / veille["n"], 1) if veille else None,
            "moyenne_7j": _moyenne(conn, station_id, 7, today),
            "moyenne_30j": _moyenne(conn, station_id, 30, today),
            "historique": [
                {
                    "date": l["date"],
                    "moyenne": round(l["somme"] / l["n"], 1),
                    "min": l["prix_min"],
                    "max": l["prix_max"],
                    "dernier": l["dernier"],
                    "releves": l["n"],
                }
                for l in lignes
            ],
        }
