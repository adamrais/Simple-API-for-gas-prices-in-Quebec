import os
import shutil
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
from app.config import CSV_PATH


def _seed_csv():
    if not os.path.exists(CSV_PATH):
        bundled = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "prix_quotidien.csv")
        if os.path.exists(bundled):
            os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
            shutil.copy(bundled, CSV_PATH)


def _save_daily_price():
    import pandas as pd
    from datetime import date
    from app.services.regie import get_prix_regie
    prix = get_prix_regie()
    if not prix:
        return
    nouvelle_ligne = pd.DataFrame([{"date": str(date.today()), "prix_pompe": prix}])
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df = pd.concat([df, nouvelle_ligne]).drop_duplicates(subset="date").reset_index(drop=True)
    else:
        df = nouvelle_ligne
    df.to_csv(CSV_PATH, index=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _seed_csv()
    scheduler = BackgroundScheduler()
    scheduler.add_job(_save_daily_price, CronTrigger(hour=14, minute=0, timezone="UTC"))
    scheduler.start()
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
