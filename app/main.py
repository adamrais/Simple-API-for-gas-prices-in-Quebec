import os
import shutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

_seed_csv()

app = FastAPI(title="API Prix Pompe")

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
