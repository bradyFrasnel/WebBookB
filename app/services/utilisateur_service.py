from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailDejaUtiliseError,
    IdentifiantsInvalidesError,
    ValidationMetierError,
)
from app.core.security import hash_password, verify_password
from app.models import Utilisateur
from app.repositories.utilisateur_repository import UtilisateurRepository
from app.schemas.utilisateur import MotDePasseUpdate, UtilisateurUpdate


class UtilisateurService:
    @staticmethod
    def update_profil(
        db: Session,
        current_user: Utilisateur,
        data: UtilisateurUpdate,
    ) -> Utilisateur:
        if data.email is not None:
            email_normalise = data.email.strip().lower()
            if email_normalise != current_user.email:
                existant = UtilisateurRepository.get_by_email(
                    db, email_normalise
                )
                if (
                    existant is not None
                    and existant.id_utilisateur != current_user.id_utilisateur
                ):
                    raise EmailDejaUtiliseError(
                        "Cette adresse email est déjà utilisée par un autre compte."
                    )
                current_user.email = email_normalise

        if "nom_utilisateur" in data.model_fields_set:
            current_user.nom_utilisateur = data.nom_utilisateur

        try:
            db.flush()
            db.commit()
            db.refresh(current_user)
            return current_user
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def change_password(
        db: Session,
        current_user: Utilisateur,
        data: MotDePasseUpdate,
    ) -> None:
        if not verify_password(
            data.ancien_mot_de_passe,
            current_user.mot_de_passe_hash,
        ):
            raise IdentifiantsInvalidesError(
                "L'ancien mot de passe est incorrect."
            )

        if data.ancien_mot_de_passe == data.nouveau_mot_de_passe:
            raise ValidationMetierError(
                "Le nouveau mot de passe doit être différent de l'ancien."
            )

        try:
            current_user.mot_de_passe_hash = hash_password(
                data.nouveau_mot_de_passe
            )
            db.flush()
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_account(
        db: Session,
        current_user: Utilisateur,
    ) -> None:
        try:
            UtilisateurRepository.delete(db, current_user)
            db.commit()
        except Exception:
            db.rollback()
            raise
