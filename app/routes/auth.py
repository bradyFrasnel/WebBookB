from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers.auth_controller import AuthController
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models import Utilisateur
from app.schemas.auth import LoginRequest, TokenResponse
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
    db: Session = Depends(get_db),
):
    return AuthController.login(
        db=db,
        email=data.email,
        mot_de_passe=data.mot_de_passe,
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
