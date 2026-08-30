import os
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.config import STATIONS_DB_PATH
from app.services.regie import _fetch_stations

RETENTION_JOURS = 31
INTERVALLE_MINUTES = 30
CARBURANTS = ("Régulier", "Super", "Diesel")
CARBURANT_DEFAUT = "Régulier"

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
    carburant  TEXT NOT NULL,
    date       TEXT NOT NULL,
    somme      REAL NOT NULL,
    n          INTEGER NOT NULL,
    prix_min   REAL NOT NULL,
    prix_max   REAL NOT NULL,
    dernier    REAL NOT NULL,
    PRIMARY KEY (station_id, carburant, date)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS prix_jour_region (
    region    TEXT NOT NULL,
    carburant TEXT NOT NULL,
    date      TEXT NOT NULL,
    somme     REAL NOT NULL,
    n         INTEGER NOT NULL,
    PRIMARY KEY (region, carburant, date)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS prix_jour_quebec (
    carburant TEXT NOT NULL,
    date      TEXT NOT NULL,
    somme     REAL NOT NULL,
    n         INTEGER NOT NULL,
    PRIMARY KEY (carburant, date)
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


_MIGRATION = """
ALTER TABLE prix_jour        RENAME TO _old_pj;
ALTER TABLE prix_jour_region RENAME TO _old_pjr;
ALTER TABLE prix_jour_quebec RENAME TO _old_pjq;
"""

_MIGRATION_COPIE = """
INSERT INTO prix_jour SELECT station_id, 'Régulier', date, somme, n, prix_min, prix_max, dernier FROM _old_pj;
INSERT INTO prix_jour_region SELECT region, 'Régulier', date, somme, n FROM _old_pjr;
INSERT INTO prix_jour_quebec SELECT 'Régulier', date, somme, n FROM _old_pjq;
DROP TABLE _old_pj;
DROP TABLE _old_pjr;
DROP TABLE _old_pjq;
"""


def init_db():
    """Crée le schéma, et migre une base antérieure à l'ajout des carburants."""
    with _connect() as conn:
        conn.executescript(_SCHEMA)
        colonnes = {r[1] for r in conn.execute("PRAGMA table_info(prix_jour)")}
        if "carburant" in colonnes:
            return
    # Base à l'ancien format : tout ce qui existe est du Régulier.
    conn = sqlite3.connect(STATIONS_DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys=OFF")
        conn.executescript(_MIGRATION)
        conn.executescript(_SCHEMA)
        conn.executescript(_MIGRATION_COPIE)
        conn.commit()
    finally:
        conn.close()


def _prix_carburants(data):
    """Un enregistrement par (station, carburant) disponible."""
    for f in data["features"]:
        props = f["properties"]
        adresse = props.get("Address")
        if not adresse:
            continue
        coords = (f.get("geometry") or {}).get("coordinates") or [None, None]
        for p in props.get("Prices", []):
            carburant = p.get("GasType")
            if carburant not in CARBURANTS or not p.get("IsAvailable"):
                continue
            try:
                prix = float(p["Price"].replace("¢", ""))
            except (KeyError, ValueError):
                continue
            yield {
                "adresse": adresse,
                "nom": props.get("Name"),
                "marque": props.get("brand"),
                "region": props.get("Region"),
                "lon": coords[0],
                "lat": coords[1],
                "carburant": carburant,
                "prix": prix,
            }


def enregistrer_releve(data=None):
    """Échantillonne le flux et met à jour l'agrégat du jour. Retourne le nombre de stations."""
    if data is None:
        data = _fetch_stations()
    releves = list(_prix_carburants(data))
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
            """INSERT INTO prix_jour (station_id, carburant, date, somme, n, prix_min, prix_max, dernier)
               VALUES (?, ?, ?, ?, 1, ?, ?, ?)
               ON CONFLICT(station_id, carburant, date) DO UPDATE SET
                 somme    = somme + excluded.somme,
                 n        = n + 1,
                 prix_min = MIN(prix_min, excluded.prix_min),
                 prix_max = MAX(prix_max, excluded.prix_max),
                 dernier  = excluded.dernier""",
            [(ids[r["adresse"]], r["carburant"], jour, r["prix"], r["prix"], r["prix"], r["prix"])
             for r in releves],
        )

        # Moyenne de ce relevé par (région, carburant), puis par carburant pour la province.
        par_region = defaultdict(list)
        par_carburant = defaultdict(list)
        for r in releves:
            par_carburant[r["carburant"]].append(r["prix"])
            if r["region"]:
                par_region[(r["region"], r["carburant"])].append(r["prix"])
        conn.executemany(
            """INSERT INTO prix_jour_region (region, carburant, date, somme, n) VALUES (?, ?, ?, ?, 1)
               ON CONFLICT(region, carburant, date) DO UPDATE SET
                 somme = somme + excluded.somme, n = n + 1""",
            [(reg, carb, jour, sum(v) / len(v)) for (reg, carb), v in par_region.items()],
        )
        conn.executemany(
            """INSERT INTO prix_jour_quebec (carburant, date, somme, n) VALUES (?, ?, ?, 1)
               ON CONFLICT(carburant, date) DO UPDATE SET
                 somme = somme + excluded.somme, n = n + 1""",
            [(carb, jour, sum(v) / len(v)) for carb, v in par_carburant.items()],
        )
    return len(releves)


def elaguer(jours=RETENTION_JOURS):
    """Supprime les jours au-delà de la fenêtre de rétention. Retourne le nombre de lignes supprimées."""
    limite = str(_today() - timedelta(days=jours - 1))
    with _connect() as conn:
        n = conn.execute("DELETE FROM prix_jour WHERE date < ?", (limite,)).rowcount
    return n


def _moyenne(conn, station_id, carburant, jours, today):
    """Moyenne des moyennes quotidiennes — chaque jour compte pareil."""
    debut = str(today - timedelta(days=jours - 1))
    r = conn.execute(
        "SELECT AVG(somme / n) m FROM prix_jour WHERE station_id=? AND carburant=? AND date>=?",
        (station_id, carburant, debut),
    ).fetchone()
    return round(r["m"], 1) if r and r["m"] is not None else None


def get_stations():
    """Liste des stations, sans prix — pour découvrir les identifiants."""
    with _connect() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT id, nom, marque, adresse, region, lat, lon FROM stations ORDER BY region, adresse")]


def get_station_par_adresse(adresse, carburant=CARBURANT_DEFAUT):
    """Même chose que get_station, mais par l'adresse — la clé fournie par le flux de la Régie."""
    with _connect() as conn:
        r = conn.execute("SELECT id FROM stations WHERE adresse=?", (adresse,)).fetchone()
    return get_station(r["id"], carburant) if r else None


def get_station(station_id, carburant=CARBURANT_DEFAUT):
    """Les 4 statistiques d'une station pour un carburant, plus son historique quotidien."""
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
               FROM prix_jour WHERE station_id=? AND carburant=? ORDER BY date""",
            (station_id, carburant),
        ).fetchall()

        par_date = {l["date"]: l for l in lignes}
        aujourdhui = par_date.get(str(today))
        veille = par_date.get(hier)

        return {
            **dict(st),
            "carburant": carburant,
            "aujourd_hui": aujourdhui["dernier"] if aujourdhui else None,
            "hier": round(veille["somme"] / veille["n"], 1) if veille else None,
            "moyenne_7j": _moyenne(conn, station_id, carburant, 7, today),
            "moyenne_30j": _moyenne(conn, station_id, carburant, 30, today),
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


def _moyenne_jours(conn, table, ou, params, jours, today):
    """Moyenne des moyennes quotidiennes sur la fenêtre — chaque jour compte pareil."""
    debut = str(today - timedelta(days=jours - 1))
    r = conn.execute(
        f"SELECT AVG(somme / n) m FROM {table} WHERE {ou} AND date >= ?",
        (*params, debut),
    ).fetchone()
    return round(r["m"], 1) if r and r["m"] is not None else None


def _valeur_jour(conn, table, ou, params, jour):
    r = conn.execute(
        f"SELECT somme / n AS v FROM {table} WHERE {ou} AND date = ?", (*params, jour)
    ).fetchone()
    return round(r["v"], 1) if r else None


def get_stats_regions_db(carburant=CARBURANT_DEFAUT):
    today = _today()
    hier = str(today - timedelta(days=1))
    ou = "region=? AND carburant=?"
    with _connect() as conn:
        regions = [r["region"] for r in conn.execute(
            "SELECT DISTINCT region FROM prix_jour_region WHERE carburant=? ORDER BY region",
            (carburant,))]
        return [
            {
                "region": reg,
                "aujourd_hui": _valeur_jour(conn, "prix_jour_region", ou, (reg, carburant), str(today)),
                "hier": _valeur_jour(conn, "prix_jour_region", ou, (reg, carburant), hier),
                "moyenne_7j": _moyenne_jours(conn, "prix_jour_region", ou, (reg, carburant), 7, today),
                "moyenne_30j": _moyenne_jours(conn, "prix_jour_region", ou, (reg, carburant), 30, today),
            }
            for reg in regions
        ]


def get_stats_quebec_db(carburant=CARBURANT_DEFAUT):
    today = _today()
    hier = str(today - timedelta(days=1))
    ou, prm = "carburant=?", (carburant,)
    with _connect() as conn:
        return {
            "aujourd_hui": _valeur_jour(conn, "prix_jour_quebec", ou, prm, str(today)),
            "hier": _valeur_jour(conn, "prix_jour_quebec", ou, prm, hier),
            "moyenne_7j": _moyenne_jours(conn, "prix_jour_quebec", ou, prm, 7, today),
            "moyenne_30j": _moyenne_jours(conn, "prix_jour_quebec", ou, prm, 30, today),
        }
