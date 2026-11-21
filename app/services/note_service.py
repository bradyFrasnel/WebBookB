from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import RessourceIntrouvableError
from app.models import Note
from app.repositories.note_repository import NoteRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.note import NoteCreate, NoteUpdate


class NoteService:
    @staticmethod
    def list_notes(
        db: Session,
        id_utilisateur: uuid.UUID,
        q: str | None = None,
        id_site: uuid.UUID | None = None,
        epingle: bool | None = None,
    ) -> list[Note]:
        if id_site is not None:
            site = SiteRepository.get_by_id(db, id_site, id_utilisateur)
            if site is None:
                raise RessourceIntrouvableError("Site introuvable.")

        return NoteRepository.get_all(
            db=db,
            id_utilisateur=id_utilisateur,
            q=q,
            id_site=id_site,
            epingle=epingle,
        )

    @staticmethod
    def get_note(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_note: uuid.UUID,
    ) -> Note:
        note = NoteRepository.get_by_id(db, id_note, id_utilisateur)
        if note is None:
            raise RessourceIntrouvableError("Note introuvable.")
        return note

    @staticmethod
    def create_note(
        db: Session,
        id_utilisateur: uuid.UUID,
        data: NoteCreate,
    ) -> Note:
        if data.id_site is not None:
            site = SiteRepository.get_by_id(db, data.id_site, id_utilisateur)
            if site is None:
                raise RessourceIntrouvableError(
                    "Le site associé est introuvable."
                )

        try:
            note = NoteRepository.create(
                db=db,
                id_utilisateur=id_utilisateur,
                titre=data.titre,
                contenu=data.contenu,
                id_site=data.id_site,
                epingle=data.epingle,
            )
            db.commit()
            return NoteService.get_note(db, id_utilisateur, note.id_note)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def update_note(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_note: uuid.UUID,
        data: NoteUpdate,
    ) -> Note:
        note = NoteRepository.get_by_id(db, id_note, id_utilisateur)
        if note is None:
            raise RessourceIntrouvableError("Note introuvable.")

        if "id_site" in data.model_fields_set:
            if data.id_site is not None:
                site = SiteRepository.get_by_id(
                    db, data.id_site, id_utilisateur
                )
                if site is None:
                    raise RessourceIntrouvableError(
                        "Le site associé est introuvable."
                    )
            note.id_site = data.id_site

        if data.titre is not None:
            note.titre = data.titre

        if data.contenu is not None:
            note.contenu = data.contenu

        if data.epingle is not None:
            note.epingle = data.epingle

        note.date_modification = datetime.now(timezone.utc)

        try:
            db.flush()
            db.commit()
            return NoteService.get_note(db, id_utilisateur, note.id_note)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def toggle_epingle(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_note: uuid.UUID,
    ) -> Note:
        note = NoteRepository.get_by_id(db, id_note, id_utilisateur)
        if note is None:
            raise RessourceIntrouvableError("Note introuvable.")

        try:
            note.epingle = not note.epingle
            note.date_modification = datetime.now(timezone.utc)
            db.flush()
            db.commit()
            return NoteService.get_note(db, id_utilisateur, note.id_note)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_note(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_note: uuid.UUID,
    ) -> None:
        note = NoteRepository.get_by_id(db, id_note, id_utilisateur)
        if note is None:
            raise RessourceIntrouvableError("Note introuvable.")

        try:
            NoteRepository.delete(db, note)
            db.commit()
        except Exception:
            db.rollback()
            raise
