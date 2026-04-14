from fastapi import FastAPI
from app.routes.predict import router as predict_router

app = FastAPI(title="API Prix Pompe")

app.include_router(predict_router)


@app.get("/")
def home():
    return {"status": "ok", "message": "API Prix Pompe en ligne!"}
