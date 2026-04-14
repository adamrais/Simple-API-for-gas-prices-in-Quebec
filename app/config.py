import os

EIA_API_KEY = "cyhLxyvxZEPi7cDWqOMgcae7e3zofdQr5u50lZHn"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(MODELS_DIR, "model.pkl")
MODEL_AR_PATH = os.path.join(MODELS_DIR, "model_ar.pkl")
LAST_KNOWN_PATH = os.path.join(MODELS_DIR, "last_known.pkl")
