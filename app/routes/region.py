from fastapi import APIRouter
from app.services.regie import get_prix_par_region

router = APIRouter()


@router.get("/regions")
def regions():
    return get_prix_par_region()
