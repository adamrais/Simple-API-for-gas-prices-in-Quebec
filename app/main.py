from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.predict import router as predict_router
from app.routes.prix_per_date import router as prix_router
from app.routes.region import router as region_router
from app.routes.graphique import router as graphique_router

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



@app.get("/")
def home():
    return {"status": "ok", "message": "API Prix Pompe en ligne!"}
