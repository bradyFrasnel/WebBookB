from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailDejaUtiliseError,
    IdentifiantsInvalidesError,
)
from app.models import Utilisateur
from app.schemas.auth import TokenResponse
from app.schemas.utilisateur import UtilisateurCreate
from app.services.auth_service import AuthService


class AuthController:
    @staticmethod
    def register(db: Session, data: UtilisateurCreate) -> Utilisateur:
        try:
            return AuthService.register(db, data)
        except EmailDejaUtiliseError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=exc.message,
            ) from exc

    @staticmethod
    def login(db: Session, email: str, mot_de_passe: str) -> TokenResponse:
        try:
            return AuthService.login(db, email, mot_de_passe)
        except IdentifiantsInvalidesError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=exc.message,
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    @staticmethod
    def me(current_user: Utilisateur) -> Utilisateur:
        return current_user

    @staticmethod
    def mot_de_passe_oublie(db: Session, email: str) -> dict[str, str]:
        AuthService.demander_reinitialisation_mot_de_passe(db, email)
        return {
            "message": "Si cette adresse email est associée à un compte, un lien de réinitialisation vous a été envoyé par email."
        }

    @staticmethod
    def reinitialiser_mot_de_passe(
        db: Session, token: str, nouveau_mot_de_passe: str
    ) -> dict[str, str]:
        try:
            AuthService.reinitialiser_mot_de_passe(
                db, token, nouveau_mot_de_passe
            )
            return {
                "message": "Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter."
            }
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
