from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailDejaUtiliseError,
    IdentifiantsInvalidesError,
    ValidationMetierError,
)
from app.models import Utilisateur
from app.schemas.utilisateur import MotDePasseUpdate, UtilisateurUpdate
from app.services.utilisateur_service import UtilisateurService


class UtilisateurController:
    @staticmethod
    def get_profil(current_user: Utilisateur) -> Utilisateur:
        return current_user

    @staticmethod
    def update_profil(
        db: Session,
        current_user: Utilisateur,
        data: UtilisateurUpdate,
    ) -> Utilisateur:
        try:
            return UtilisateurService.update_profil(db, current_user, data)
        except EmailDejaUtiliseError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=exc.message,
            ) from exc

    @staticmethod
    def change_password(
        db: Session,
        current_user: Utilisateur,
        data: MotDePasseUpdate,
    ) -> dict[str, str]:
        try:
            UtilisateurService.change_password(db, current_user, data)
            return {"message": "Mot de passe modifié avec succès."}
        except IdentifiantsInvalidesError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exc.message,
            ) from exc
        except ValidationMetierError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exc.message,
            ) from exc

    @staticmethod
    def delete_account(
        db: Session,
        current_user: Utilisateur,
    ) -> None:
        UtilisateurService.delete_account(db, current_user)
