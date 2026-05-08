import os
import shutil
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.routes.predict import router as predict_router
from app.routes.prix import router as prix_router
from app.routes.region import router as region_router
from app.routes.graphique import router as graphique_router
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
    from datetime import date
    from app.services.regie import get_prix_regie
    today = str(date.today())
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
    df.to_csv(CSV_PATH, index=False)
    logger.info(f"[scheduler] Saved price {prix}¢ for {today}")


def _save_daily_regions():
    import pandas as pd
    from datetime import date
    from app.services.regie import get_prix_par_region
    today = str(date.today())
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
    df.to_csv(CSV_REGIONS_PATH, index=False)
    logger.info(f"[scheduler] Saved prices for {len(regions)} regions on {today}")


def _save_if_missing_today():
    import pandas as pd
    from datetime import date
    today = str(date.today())
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        if today in df["date"].values:
            return
    logger.info("[scheduler] Today's price missing on startup — fetching now")
    _save_daily_price()


def _save_if_missing_today_regions():
    import pandas as pd
    from datetime import date
    today = str(date.today())
    if os.path.exists(CSV_REGIONS_PATH):
        df = pd.read_csv(CSV_REGIONS_PATH)
        if today in df["date"].values:
            return
    logger.info("[scheduler] Today's region prices missing on startup — fetching now")
    _save_daily_regions()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _seed_csv()
    _save_if_missing_today()
    _save_if_missing_today_regions()
    scheduler = BackgroundScheduler()
    scheduler.add_job(_save_daily_price, CronTrigger(hour=10, minute=0, timezone="America/Montreal"))
    scheduler.add_job(_save_daily_regions, CronTrigger(hour=10, minute=1, timezone="America/Montreal"))
    scheduler.start()
    logger.info("[scheduler] Started — daily price jobs at 10:00/10:01 America/Montreal")
    yield
    scheduler.shutdown()


app = FastAPI(title="API Prix Pompe", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(predict_router)
app.include_router(prix_router)
app.include_router(region_router)
app.include_router(graphique_router)

app.mount("/static", StaticFiles(directory="docs/static"), name="static")
app.mount("/", StaticFiles(directory="docs", html=True), name="templates")
