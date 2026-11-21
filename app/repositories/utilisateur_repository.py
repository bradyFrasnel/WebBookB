import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Utilisateur


class UtilisateurRepository:
    @staticmethod
    def get_by_id(db: Session, id_utilisateur: uuid.UUID) -> Utilisateur | None:
        stmt = select(Utilisateur).where(
            Utilisateur.id_utilisateur == id_utilisateur
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Utilisateur | None:
        stmt = select(Utilisateur).where(Utilisateur.email == email)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(
        db: Session,
        email: str,
        mot_de_passe_hash: str,
        nom_utilisateur: str | None = None,
    ) -> Utilisateur:
        utilisateur = Utilisateur(
            email=email,
            nom_utilisateur=nom_utilisateur,
            mot_de_passe_hash=mot_de_passe_hash,
        )
        db.add(utilisateur)
        db.flush()
        return utilisateur

    @staticmethod
    def delete(db: Session, utilisateur: Utilisateur) -> None:
        db.delete(utilisateur)
        db.flush()
