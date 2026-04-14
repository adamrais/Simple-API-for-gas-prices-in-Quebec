import pickle
import numpy as np
from datetime import date, timedelta
from app.config import MODEL_PATH, MODEL_AR_PATH, LAST_KNOWN_PATH

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(MODEL_AR_PATH, "rb") as f:
    model_ar = pickle.load(f)

with open(LAST_KNOWN_PATH, "rb") as f:
    last_known = pickle.load(f)


def predict_today(c, saison, wti_lag1, wti_lag2, c_lag1):
    x = np.array([[c, saison, wti_lag1, wti_lag2, c_lag1]])
    return model.predict(x)[0]


def predict_future(prix_aujourdhui, jours):
    N_LAGS = 4
    window = list(last_known[1:]) + [prix_aujourdhui]
    resultats = []

    for j in range(1, jours + 1):
        x_ar = np.array([window[-1], window[-2], window[-3], window[-4]]).reshape(1, -1)
        preds = np.array([arbre.predict(x_ar)[0] for arbre in model_ar.estimators_])
        moy  = round(float(np.percentile(preds, 50)), 2)
        opt  = round(float(np.percentile(preds, 95)), 2)
        pess = round(float(np.percentile(preds, 5)),  2)

        resultats.append({
            "date": str(date.today() + timedelta(days=j)),
            "optimiste": pess,
            "moyen": moy,
            "pessimiste": opt,
        })

        window.append(moy)
        if len(window) > N_LAGS:
            window = window[-N_LAGS:]

    return resultats
