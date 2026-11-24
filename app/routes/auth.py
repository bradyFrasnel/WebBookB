from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.controllers.auth_controller import AuthController
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models import Utilisateur
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    MotDePasseOublieRequest,
    ReinitialiserMotDePasseRequest,
    TokenResponse,
)
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurResponse

router = APIRouter(prefix="/api/auth", tags=["Authentification"])


@router.post(
    "/register",
    response_model=UtilisateurResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte utilisateur",
)
def register(
    data: UtilisateurCreate,
    db: Session = Depends(get_db),
):
    return AuthController.register(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Se connecter et obtenir un token JWT",
)
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return AuthController.login(
        db=db,
        email=data.email,
        mot_de_passe=data.mot_de_passe,
        request=request,
    )


@router.get(
    "/me",
    response_model=UtilisateurResponse,
    summary="Obtenir les informations de l'utilisateur connecté",
)
def me(
    current_user: Utilisateur = Depends(get_current_user),
):
    return AuthController.me(current_user)


@router.post(
    "/mot-de-passe-oublie",
    response_model=MessageResponse,
    summary="Demander un lien de réinitialisation de mot de passe par email",
)
def mot_de_passe_oublie(
    data: MotDePasseOublieRequest,
    db: Session = Depends(get_db),
):
    return AuthController.mot_de_passe_oublie(db=db, email=data.email)


@router.post(
    "/reinitialiser-mot-de-passe",
    response_model=MessageResponse,
    summary="Définir un nouveau mot de passe avec un lien de réinitialisation",
)
def reinitialiser_mot_de_passe(
    data: ReinitialiserMotDePasseRequest,
    db: Session = Depends(get_db),
):
    return AuthController.reinitialiser_mot_de_passe(
        db=db,
        token=data.token,
        nouveau_mot_de_passe=data.nouveau_mot_de_passe,
    )
