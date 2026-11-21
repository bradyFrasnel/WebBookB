import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, joinedload

from app.models import HistoriqueConsultation


class HistoriqueRepository:
    @staticmethod
    def get_all(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_site: uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[HistoriqueConsultation]:
        stmt = (
            select(HistoriqueConsultation)
            .options(joinedload(HistoriqueConsultation.site))
            .where(HistoriqueConsultation.id_utilisateur == id_utilisateur)
        )

        if id_site is not None:
            stmt = stmt.where(HistoriqueConsultation.id_site == id_site)

        stmt = stmt.order_by(
            HistoriqueConsultation.date_consultation.desc()
        ).limit(limit)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_by_id(
        db: Session,
        id_consultation: uuid.UUID,
        id_utilisateur: uuid.UUID,
    ) -> HistoriqueConsultation | None:
        stmt = (
            select(HistoriqueConsultation)
            .options(joinedload(HistoriqueConsultation.site))
            .where(
                HistoriqueConsultation.id_consultation == id_consultation,
                HistoriqueConsultation.id_utilisateur == id_utilisateur,
            )
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def count_all(db: Session, id_utilisateur: uuid.UUID) -> int:
        stmt = select(func.count(HistoriqueConsultation.id_consultation)).where(
            HistoriqueConsultation.id_utilisateur == id_utilisateur
        )
        return int(db.execute(stmt).scalar_one())

    @staticmethod
    def create(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_site: uuid.UUID,
    ) -> HistoriqueConsultation:
        consultation = HistoriqueConsultation(
            id_utilisateur=id_utilisateur,
            id_site=id_site,
        )
        db.add(consultation)
        db.flush()
        return consultation

    @staticmethod
    def delete(db: Session, consultation: HistoriqueConsultation) -> None:
        db.delete(consultation)
        db.flush()

    @staticmethod
    def clear_all(db: Session, id_utilisateur: uuid.UUID) -> None:
        stmt = delete(HistoriqueConsultation).where(
            HistoriqueConsultation.id_utilisateur == id_utilisateur
        )
        db.execute(stmt)
        db.flush()
