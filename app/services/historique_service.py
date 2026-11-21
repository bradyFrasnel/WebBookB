import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import RessourceIntrouvableError
from app.models import HistoriqueConsultation
from app.repositories.historique_repository import HistoriqueRepository
from app.repositories.site_repository import SiteRepository


class HistoriqueService:
    @staticmethod
    def list_historique(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_site: uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[HistoriqueConsultation]:
        if id_site is not None:
            site = SiteRepository.get_by_id(db, id_site, id_utilisateur)
            if site is None:
                raise RessourceIntrouvableError("Site introuvable.")

        return HistoriqueRepository.get_all(
            db=db,
            id_utilisateur=id_utilisateur,
            id_site=id_site,
            limit=limit,
        )

    @staticmethod
    def delete_consultation(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_consultation: uuid.UUID,
    ) -> None:
        consultation = HistoriqueRepository.get_by_id(
            db, id_consultation, id_utilisateur
        )
        if consultation is None:
            raise RessourceIntrouvableError(
                "Entrée d'historique introuvable."
            )

        try:
            HistoriqueRepository.delete(db, consultation)
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def clear_historique(
        db: Session,
        id_utilisateur: uuid.UUID,
        reinitialiser_compteurs: bool = True,
    ) -> None:
        try:
            HistoriqueRepository.clear_all(db, id_utilisateur)
            if reinitialiser_compteurs:
                SiteRepository.reset_consultations(db, id_utilisateur)
            db.commit()
        except Exception:
            db.rollback()
            raise
