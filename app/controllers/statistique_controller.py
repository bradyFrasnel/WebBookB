from sqlalchemy.orm import Session

from app.models import Utilisateur
from app.schemas.statistique import StatistiquesResponse
from app.services.statistique_service import StatistiqueService


class StatistiqueController:
    @staticmethod
    def get_statistiques(
        db: Session,
        current_user: Utilisateur,
    ) -> StatistiquesResponse:
        return StatistiqueService.get_statistiques(
            db, current_user.id_utilisateur
        )
