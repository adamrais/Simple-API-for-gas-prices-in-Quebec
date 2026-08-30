import os
import shutil
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.routes.predict import router as predict_router
from app.routes.prix import router as prix_router
from app.routes.region import router as region_router
from app.routes.graphique import router as graphique_router
from app.routes.stations import router as stations_router
from app.routes.sante import router as sante_router
from app.config import CSV_PATH, CSV_REGIONS_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _seed_csv():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    if not os.path.exists(CSV_PATH):
        bundled = os.path.join(data_dir, "prix_quotidien.csv")
        if os.path.exists(bundled):
            shutil.copy(bundled, CSV_PATH)
            logger.info(f"[csv] Seeded CSV from bundled data to {CSV_PATH}")
    if not os.path.exists(CSV_REGIONS_PATH):
        bundled_regions = os.path.join(data_dir, "prix_quotidien_regions.csv")
        if os.path.exists(bundled_regions):
            shutil.copy(bundled_regions, CSV_REGIONS_PATH)
            logger.info(f"[csv] Seeded regions CSV from bundled data to {CSV_REGIONS_PATH}")


def _save_daily_price():
    import pandas as pd
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from app.services.regie import get_prix_regie
    today = str(datetime.now(ZoneInfo("America/Montreal")).date())
    logger.info(f"[scheduler] Fetching daily price for {today}")
    prix = get_prix_regie()
    if not prix:
        logger.warning("[scheduler] No price returned from Régie, skipping.")
        return
    nouvelle_ligne = pd.DataFrame([{"date": today, "prix_pompe": prix}])
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df = pd.concat([df, nouvelle_ligne]).drop_duplicates(subset="date").reset_index(drop=True)
    else:
        df = nouvelle_ligne
    tmp = CSV_PATH + ".tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, CSV_PATH)
    logger.info(f"[scheduler] Saved price {prix}¢ for {today}")


def _save_daily_regions():
    import pandas as pd
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from app.services.regie import get_prix_par_region
    today = str(datetime.now(ZoneInfo("America/Montreal")).date())
    logger.info(f"[scheduler] Fetching daily region prices for {today}")
    regions = get_prix_par_region()
    if not regions:
        logger.warning("[scheduler] No region prices returned, skipping.")
        return
    nouvelles_lignes = pd.DataFrame([
        {"date": today, "region": region, "prix": prix}
        for region, prix in regions.items()
    ])
    if os.path.exists(CSV_REGIONS_PATH):
        df = pd.read_csv(CSV_REGIONS_PATH)
        df = pd.concat([df, nouvelles_lignes]).drop_duplicates(subset=["date", "region"]).reset_index(drop=True)
    else:
        df = nouvelles_lignes
    tmp = CSV_REGIONS_PATH + ".tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, CSV_REGIONS_PATH)
    logger.info(f"[scheduler] Saved prices for {len(regions)} regions on {today}")


def _echantillonner_stations():
    from app.services.stations_db import enregistrer_releve
    try:
        n = enregistrer_releve()
    except Exception as e:
        logger.error(f"[scheduler] Échantillonnage stations échoué: {e}")
        return
    logger.info(f"[scheduler] Relevé enregistré pour {n} stations")


def _releve_marche():
    from app.services.stations_db import enregistrer_marche
    try:
        ok = enregistrer_marche()
    except Exception as e:
        logger.error(f"[scheduler] Relevé marché échoué: {e}")
        return
    logger.info("[scheduler] Marché enregistré" if ok else "[scheduler] Marché indisponible")


def _releve_marche_si_manquant():
    from app.services.stations_db import marche_du_jour_present
    try:
        if marche_du_jour_present():
            return
    except Exception as e:
        logger.error(f"[scheduler] Vérification marché échouée: {e}")
        return
    logger.info("[scheduler] Marché du jour absent au démarrage — relevé immédiat")
    _releve_marche()


def _elaguer_stations():
    from app.services.stations_db import elaguer, RETENTION_JOURS
    try:
        n = elaguer()
    except Exception as e:
        logger.error(f"[scheduler] Élagage stations échoué: {e}")
        return
    logger.info(f"[scheduler] Élagage: {n} lignes supprimées (rétention {RETENTION_JOURS} jours)")


def _trigger_github_sync():
    import requests
    token = os.environ.get("GITHUB_SYNC_TOKEN")
    repo = os.environ.get("GITHUB_SYNC_REPO", "adamrais/Simple-API-for-gas-prices-in-Quebec")
    if not token:
        logger.warning("[scheduler] GITHUB_SYNC_TOKEN not set, skipping CSV backup trigger.")
        return
    logger.info(f"[scheduler] Triggering CSV backup workflow on {repo}")
    try:
        r = requests.post(
            f"https://api.github.com/repos/{repo}/dispatches",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={"event_type": "csv-updated"},
            timeout=30,
        )
    except requests.RequestException as e:
        logger.error(f"[scheduler] CSV backup trigger failed: {e}")
        return
    if r.status_code == 204:
        logger.info("[scheduler] CSV backup workflow triggered")
    else:
        logger.error(f"[scheduler] CSV backup trigger returned {r.status_code}: {r.text[:200]}")


def _save_if_missing_today():
    import pandas as pd
    from datetime import datetime
    from zoneinfo import ZoneInfo
    today = str(datetime.now(ZoneInfo("America/Montreal")).date())
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        if today in df["date"].values:
            return
    logger.info("[scheduler] Today's price missing on startup — fetching now")
    _save_daily_price()


def _save_if_missing_today_regions():
    import pandas as pd
    from datetime import datetime
    from zoneinfo import ZoneInfo
    today = str(datetime.now(ZoneInfo("America/Montreal")).date())
    if os.path.exists(CSV_REGIONS_PATH):
        df = pd.read_csv(CSV_REGIONS_PATH)
        if today in df["date"].values:
            return
    logger.info("[scheduler] Today's region prices missing on startup — fetching now")
    _save_daily_regions()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _seed_csv()
    from app.services.stations_db import init_db, reprendre_marche_historique, INTERVALLE_MINUTES
    init_db()
    try:
        logger.info(f"[marche] Historique amorcé: {reprendre_marche_historique()} jours")
    except Exception as e:
        logger.error(f"[marche] Amorçage échoué: {e}")
    _save_if_missing_today()
    _save_if_missing_today_regions()
    _elaguer_stations()
    _releve_marche_si_manquant()
    scheduler = BackgroundScheduler()
    scheduler.add_job(_save_daily_price, CronTrigger(hour=10, minute=0, timezone="America/Montreal"))
    scheduler.add_job(_save_daily_regions, CronTrigger(hour=10, minute=1, timezone="America/Montreal"))
    scheduler.add_job(_trigger_github_sync, CronTrigger(hour=10, minute=5, timezone="America/Montreal"))
    scheduler.add_job(_echantillonner_stations,
                      CronTrigger(minute=f"*/{INTERVALLE_MINUTES}", timezone="America/Montreal"))
    scheduler.add_job(_elaguer_stations, CronTrigger(hour=3, minute=30, timezone="America/Montreal"))
    scheduler.add_job(_releve_marche, CronTrigger(hour=17, minute=0, timezone="America/Montreal"))
    scheduler.start()
    # Premier relevé hors du thread principal : ne retarde pas la disponibilité
    # de l'app au démarrage (le redéploiement Railway est déjà une fenêtre 502).
    scheduler.add_job(_echantillonner_stations)
    logger.info(
        "[scheduler] Started — daily price jobs at 10:00/10:01, CSV backup trigger at 10:05, "
        f"stations sampled every {INTERVALLE_MINUTES} min, market at 17:00, pruning at 03:30 America/Montreal")
    yield
    scheduler.shutdown()


app = FastAPI(title="API Prix Pompe", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# En dessous de 1000 octets, la compression coûte plus qu'elle ne rapporte.
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(predict_router)
app.include_router(prix_router)
app.include_router(region_router)
app.include_router(graphique_router)
app.include_router(stations_router)
app.include_router(sante_router)

app.mount("/static", StaticFiles(directory="docs/static"), name="static")
app.mount("/", StaticFiles(directory="docs", html=True), name="templates")
