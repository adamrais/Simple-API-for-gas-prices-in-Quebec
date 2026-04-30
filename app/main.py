from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.predict import router as predict_router

app = FastAPI(title="API Prix Pompe")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(predict_router)


@app.get("/")
def home():
    return {"status": "ok", "message": "API Prix Pompe en ligne!"}
