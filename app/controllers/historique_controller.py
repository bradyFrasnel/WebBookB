import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import RessourceIntrouvableError
from app.models import HistoriqueConsultation, Utilisateur
from app.services.historique_service import HistoriqueService


class HistoriqueController:
    @staticmethod
    def list_historique(
        db: Session,
        current_user: Utilisateur,
        id_site: uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[HistoriqueConsultation]:
        try:
            return HistoriqueService.list_historique(
                db=db,
                id_utilisateur=current_user.id_utilisateur,
                id_site=id_site,
                limit=limit,
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def delete_consultation(
        db: Session,
        current_user: Utilisateur,
        id_consultation: uuid.UUID,
    ) -> None:
        try:
            HistoriqueService.delete_consultation(
                db=db,
                id_utilisateur=current_user.id_utilisateur,
                id_consultation=id_consultation,
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def clear_historique(
        db: Session,
        current_user: Utilisateur,
        reinitialiser_compteurs: bool = True,
    ) -> None:
        HistoriqueService.clear_historique(
            db=db,
            id_utilisateur=current_user.id_utilisateur,
            reinitialiser_compteurs=reinitialiser_compteurs,
        )
