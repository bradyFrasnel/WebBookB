import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers.categorie_controller import CategorieController
from app.controllers.site_controller import SiteController
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models import Utilisateur
from app.schemas.categorie import (
    CategorieCreate,
    CategorieResponse,
    CategorieUpdate,
)
from app.schemas.site import SiteResponse

router = APIRouter(prefix="/api/categories", tags=["Catégories"])


@router.get(
    "",
    response_model=list[CategorieResponse],
    summary="Lister toutes les catégories de l'utilisateur",
)
def list_categories(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return CategorieController.list_categories(db, current_user)


@router.get(
    "/{id_categorie}",
    response_model=CategorieResponse,
    summary="Obtenir le détail d'une catégorie",
)
def get_categorie(
    id_categorie: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return CategorieController.get_categorie(db, current_user, id_categorie)


@router.get(
    "/{id_categorie}/sites",
    response_model=list[SiteResponse],
    summary="Consulter les sites associés à une catégorie",
)
def list_sites_by_categorie(
    id_categorie: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return SiteController.list_sites(
        db=db,
        current_user=current_user,
        id_categorie=id_categorie,
    )


@router.post(
    "",
    response_model=CategorieResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une catégorie personnalisée",
)
def create_categorie(
    data: CategorieCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return CategorieController.create_categorie(db, current_user, data)


@router.patch(
    "/{id_categorie}",
    response_model=CategorieResponse,
    summary="Modifier le nom d'une catégorie",
)
def update_categorie(
    id_categorie: uuid.UUID,
    data: CategorieUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return CategorieController.update_categorie(
        db, current_user, id_categorie, data
    )


@router.delete(
    "/{id_categorie}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une catégorie (avec réaffectation obligatoire si elle contient des sites)",
)
def delete_categorie(
    id_categorie: uuid.UUID,
    nouvelle_categorie_id: uuid.UUID | None = Query(
        default=None,
        description="ID de la catégorie vers laquelle réaffecter les sites avant suppression",
    ),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    CategorieController.delete_categorie(
        db=db,
        current_user=current_user,
        id_categorie=id_categorie,
        nouvelle_categorie_id=nouvelle_categorie_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
