import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Note


class NoteRepository:
    @staticmethod
    def get_all(
        db: Session,
        id_utilisateur: uuid.UUID,
        q: str | None = None,
        id_site: uuid.UUID | None = None,
        epingle: bool | None = None,
    ) -> list[Note]:
        stmt = (
            select(Note)
            .options(joinedload(Note.site))
            .where(Note.id_utilisateur == id_utilisateur)
        )

        if id_site is not None:
            stmt = stmt.where(Note.id_site == id_site)

        if epingle is not None:
            stmt = stmt.where(Note.epingle == epingle)

        if q is not None and q.strip():
            terme = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Note.titre.ilike(terme),
                    Note.contenu.ilike(terme),
                )
            )

        stmt = stmt.order_by(
            Note.epingle.desc(),
            Note.date_modification.desc(),
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_by_id(
        db: Session,
        id_note: uuid.UUID,
        id_utilisateur: uuid.UUID,
    ) -> Note | None:
        stmt = (
            select(Note)
            .options(joinedload(Note.site))
            .where(
                Note.id_note == id_note,
                Note.id_utilisateur == id_utilisateur,
            )
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def count_all(db: Session, id_utilisateur: uuid.UUID) -> int:
        stmt = select(func.count(Note.id_note)).where(
            Note.id_utilisateur == id_utilisateur
        )
        return int(db.execute(stmt).scalar_one())

    @staticmethod
    def create(
        db: Session,
        id_utilisateur: uuid.UUID,
        titre: str,
        contenu: str,
        id_site: uuid.UUID | None = None,
        epingle: bool = False,
    ) -> Note:
        note = Note(
            id_utilisateur=id_utilisateur,
            id_site=id_site,
            titre=titre,
            contenu=contenu,
            epingle=epingle,
        )
        db.add(note)
        db.flush()
        return note

    @staticmethod
    def delete(db: Session, note: Note) -> None:
        db.delete(note)
        db.flush()
