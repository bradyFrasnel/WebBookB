import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import RessourceIntrouvableError
from app.models import Note, Utilisateur
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.note_service import NoteService


class NoteController:
    @staticmethod
    def list_notes(
        db: Session,
        current_user: Utilisateur,
        q: str | None = None,
        id_site: uuid.UUID | None = None,
        epingle: bool | None = None,
    ) -> list[Note]:
        try:
            return NoteService.list_notes(
                db=db,
                id_utilisateur=current_user.id_utilisateur,
                q=q,
                id_site=id_site,
                epingle=epingle,
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def get_note(
        db: Session,
        current_user: Utilisateur,
        id_note: uuid.UUID,
    ) -> Note:
        try:
            return NoteService.get_note(
                db, current_user.id_utilisateur, id_note
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def create_note(
        db: Session,
        current_user: Utilisateur,
        data: NoteCreate,
    ) -> Note:
        try:
            return NoteService.create_note(
                db, current_user.id_utilisateur, data
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def update_note(
        db: Session,
        current_user: Utilisateur,
        id_note: uuid.UUID,
        data: NoteUpdate,
    ) -> Note:
        try:
            return NoteService.update_note(
                db, current_user.id_utilisateur, id_note, data
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def toggle_epingle(
        db: Session,
        current_user: Utilisateur,
        id_note: uuid.UUID,
    ) -> Note:
        try:
            return NoteService.toggle_epingle(
                db, current_user.id_utilisateur, id_note
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def delete_note(
        db: Session,
        current_user: Utilisateur,
        id_note: uuid.UUID,
    ) -> None:
        try:
            NoteService.delete_note(db, current_user.id_utilisateur, id_note)
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc
