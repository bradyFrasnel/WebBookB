from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailDejaUtiliseError,
    EnvoiEmailError,
    IdentifiantsInvalidesError,
    RessourceIntrouvableError,
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
        try:
            destinataire = AuthService.demander_reinitialisation_mot_de_passe(
                db, email
            )
            return {
                "message": f"Un lien vous a été envoyé à l'adresse {destinataire}."
            }
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc
        except EnvoiEmailError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=exc.message,
            ) from exc

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
