import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers.note_controller import NoteController
from app.controllers.site_controller import SiteController
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models import Utilisateur
from app.schemas.note import NoteResponse
from app.schemas.site import SiteCreate, SiteResponse, SiteUpdate

router = APIRouter(prefix="/api/sites", tags=["Sites"])


@router.get(
    "",
    response_model=list[SiteResponse],
    summary="Lister et rechercher les sites de l'utilisateur",
)
def list_sites(
    q: str | None = Query(
        default=None,
        max_length=200,
        description="Recherche par nom, URL ou note personnelle du site",
    ),
    id_categorie: uuid.UUID | None = Query(
        default=None,
        description="Filtrer par identifiant de catégorie",
    ),
    favori: bool | None = Query(
        default=None,
        description="Filtrer uniquement les favoris (true) ou non-favoris (false)",
    ),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return SiteController.list_sites(
        db=db,
        current_user=current_user,
        q=q,
        id_categorie=id_categorie,
        favori=favori,
    )


@router.get(
    "/favoris",
    response_model=list[SiteResponse],
    summary="Lister tous les sites favoris de l'utilisateur",
)
def list_favoris(
    q: str | None = Query(
        default=None,
        max_length=200,
        description="Recherche parmi les favoris par nom, URL ou note",
    ),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return SiteController.list_sites(
        db=db,
        current_user=current_user,
        q=q,
        favori=True,
    )


@router.get(
    "/recents",
    response_model=list[SiteResponse],
    summary="Lister les sites récemment consultés",
)
def list_recent_sites(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Nombre maximum de sites récents à retourner",
    ),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return SiteController.list_recent_sites(db, current_user, limit=limit)


@router.get(
    "/{id_site}",
    response_model=SiteResponse,
    summary="Consulter le détail d'un site",
)
def get_site(
    id_site: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return SiteController.get_site(db, current_user, id_site)


@router.get(
    "/{id_site}/notes",
    response_model=list[NoteResponse],
    summary="Lister toutes les notes personnelles attachées à un site",
)
def list_notes_by_site(
    id_site: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return NoteController.list_notes(
        db=db,
        current_user=current_user,
        id_site=id_site,
    )


@router.post(
    "",
    response_model=SiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un nouveau site",
)
def create_site(
    data: SiteCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return SiteController.create_site(db, current_user, data)


@router.post(
    "/{id_site}/consulter",
    response_model=SiteResponse,
    summary="Enregistrer une consultation du site dans l'historique",
)
def record_visit(
    id_site: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return SiteController.record_visit(db, current_user, id_site)


@router.patch(
    "/{id_site}",
    response_model=SiteResponse,
    summary="Modifier un site existant",
)
def update_site(
    id_site: uuid.UUID,
    data: SiteUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return SiteController.update_site(db, current_user, id_site, data)


@router.patch(
    "/{id_site}/favori",
    response_model=SiteResponse,
    summary="Ajouter ou retirer un site des favoris (bascule)",
)
def toggle_favori(
    id_site: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return SiteController.toggle_favori(db, current_user, id_site)


@router.delete(
    "/{id_site}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un site",
)
def delete_site(
    id_site: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    SiteController.delete_site(db, current_user, id_site)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
