import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers.note_controller import NoteController
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models import Utilisateur
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(prefix="/api/notes", tags=["Notes personnelles"])


@router.get(
    "",
    response_model=list[NoteResponse],
    summary="Lister et rechercher les notes personnelles",
)
def list_notes(
    q: str | None = Query(
        default=None,
        description="Recherche par titre ou contenu de la note",
    ),
    id_site: uuid.UUID | None = Query(
        default=None,
        description="Filtrer les notes rattachées à un site particulier",
    ),
    epingle: bool | None = Query(
        default=None,
        description="Filtrer les notes épinglées (true) ou non (false)",
    ),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return NoteController.list_notes(
        db=db,
        current_user=current_user,
        q=q,
        id_site=id_site,
        epingle=epingle,
    )


@router.get(
    "/{id_note}",
    response_model=NoteResponse,
    summary="Consulter le détail d'une note personnelle",
)
def get_note(
    id_note: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return NoteController.get_note(db, current_user, id_note)


@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle note personnelle",
)
def create_note(
    data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return NoteController.create_note(db, current_user, data)


@router.patch(
    "/{id_note}",
    response_model=NoteResponse,
    summary="Modifier une note personnelle",
)
def update_note(
    id_note: uuid.UUID,
    data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return NoteController.update_note(db, current_user, id_note, data)


@router.patch(
    "/{id_note}/epingler",
    response_model=NoteResponse,
    summary="Épingler ou désépingler une note (bascule)",
)
def toggle_epingle(
    id_note: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return NoteController.toggle_epingle(db, current_user, id_note)


@router.delete(
    "/{id_note}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une note personnelle",
)
def delete_note(
    id_note: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    NoteController.delete_note(db, current_user, id_note)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
