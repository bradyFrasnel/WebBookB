from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.audit_logger import log_security_event
from app.core.exceptions import (
    EmailDejaUtiliseError,
    EnvoiEmailError,
    IdentifiantsInvalidesError,
    RessourceIntrouvableError,
)
from app.core.rate_limit import get_client_ip, login_tracker
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
    def login(
        db: Session,
        email: str,
        mot_de_passe: str,
        request: Request | None = None,
    ) -> TokenResponse | JSONResponse:
        client_ip = get_client_ip(request) if request is not None else "local"
        try:
            token_resp = AuthService.login(db, email, mot_de_passe)
            login_tracker.record_success(client_ip)
            return token_resp
        except IdentifiantsInvalidesError as exc:
            locked, retry_after, remaining = login_tracker.record_failure(
                client_ip
            )
            if locked:
                log_security_event(
                    "LOGIN_LOCKOUT_TRIGGERED",
                    ip=client_ip,
                    retry_after=retry_after,
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={"Retry-After": str(retry_after)},
                    content={
                        "detail": "Trop de tentatives infructueuses (5/5). Veuillez patienter 5 minutes avant de réessayer.",
                        "retry_after": retry_after,
                    },
                )
            plural = "s" if remaining > 1 else ""
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{exc.message} ({remaining} tentative{plural} restante{plural})",
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
