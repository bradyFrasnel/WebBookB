from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.statistique_controller import StatistiqueController
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models import Utilisateur
from app.schemas.statistique import StatistiquesResponse

router = APIRouter(prefix="/api/statistiques", tags=["Statistiques"])


@router.get(
    "",
    response_model=StatistiquesResponse,
    summary="Obtenir les statistiques du tableau de bord",
)
def get_statistiques(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return StatistiqueController.get_statistiques(db, current_user)
