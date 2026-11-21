from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers.utilisateur_controller import UtilisateurController
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models import Utilisateur
from app.schemas.utilisateur import (
    MotDePasseUpdate,
    UtilisateurResponse,
    UtilisateurUpdate,
)

router = APIRouter(prefix="/api/utilisateurs", tags=["Profil Utilisateur"])


@router.get(
    "/me",
    response_model=UtilisateurResponse,
    summary="Consulter le profil de l'utilisateur connecté",
)
def get_profil(
    current_user: Utilisateur = Depends(get_current_user),
):
    return UtilisateurController.get_profil(current_user)


@router.patch(
    "/me",
    response_model=UtilisateurResponse,
    summary="Modifier son profil (nom/pseudo ou email)",
)
def update_profil(
    data: UtilisateurUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return UtilisateurController.update_profil(db, current_user, data)


@router.patch(
    "/me/mot-de-passe",
    summary="Changer son mot de passe",
)
def change_password(
    data: MotDePasseUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return UtilisateurController.change_password(db, current_user, data)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer son compte utilisateur et toutes ses données",
)
def delete_account(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    UtilisateurController.delete_account(db, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
