import uuid

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, joinedload

from app.models import Site


class SiteRepository:
    @staticmethod
    def get_all(
        db: Session,
        id_utilisateur: uuid.UUID,
        q: str | None = None,
        id_categorie: uuid.UUID | None = None,
        favori: bool | None = None,
    ) -> list[Site]:
        stmt = (
            select(Site)
            .options(joinedload(Site.categorie))
            .where(Site.id_utilisateur == id_utilisateur)
        )

        if id_categorie is not None:
            stmt = stmt.where(Site.id_categorie == id_categorie)

        if favori is not None:
            stmt = stmt.where(Site.favori == favori)

        if q is not None and q.strip():
            terme = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Site.nom.ilike(terme),
                    Site.url.ilike(terme),
                    Site.note_personnelle.ilike(terme),
                )
            )

        stmt = stmt.order_by(Site.favori.desc(), Site.date_creation.desc())
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_recently_visited(
        db: Session,
        id_utilisateur: uuid.UUID,
        limit: int = 10,
    ) -> list[Site]:
        stmt = (
            select(Site)
            .options(joinedload(Site.categorie))
            .where(
                Site.id_utilisateur == id_utilisateur,
                Site.derniere_consultation.is_not(None),
            )
            .order_by(Site.derniere_consultation.desc())
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_by_id(
        db: Session,
        id_site: uuid.UUID,
        id_utilisateur: uuid.UUID,
    ) -> Site | None:
        stmt = (
            select(Site)
            .options(joinedload(Site.categorie))
            .where(
                Site.id_site == id_site,
                Site.id_utilisateur == id_utilisateur,
            )
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_by_url_ci(
        db: Session,
        id_utilisateur: uuid.UUID,
        url: str,
    ) -> Site | None:
        stmt = select(Site).where(
            Site.id_utilisateur == id_utilisateur,
            func.lower(Site.url) == url.lower(),
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def count_all(db: Session, id_utilisateur: uuid.UUID) -> int:
        stmt = select(func.count(Site.id_site)).where(
            Site.id_utilisateur == id_utilisateur
        )
        return int(db.execute(stmt).scalar_one())

    @staticmethod
    def count_favoris(db: Session, id_utilisateur: uuid.UUID) -> int:
        stmt = select(func.count(Site.id_site)).where(
            Site.id_utilisateur == id_utilisateur,
            Site.favori.is_(True),
        )
        return int(db.execute(stmt).scalar_one())

    @staticmethod
    def create(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_categorie: uuid.UUID,
        nom: str,
        url: str,
        icone_url: str | None,
        favori: bool = False,
        note_personnelle: str | None = None,
    ) -> Site:
        site = Site(
            id_utilisateur=id_utilisateur,
            id_categorie=id_categorie,
            nom=nom,
            url=url,
            icone_url=icone_url,
            favori=favori,
            note_personnelle=note_personnelle,
        )
        db.add(site)
        db.flush()
        return site

    @staticmethod
    def reset_consultations(
        db: Session,
        id_utilisateur: uuid.UUID,
    ) -> None:
        stmt = (
            update(Site)
            .where(Site.id_utilisateur == id_utilisateur)
            .values(derniere_consultation=None, nombre_consultations=0)
        )
        db.execute(stmt)
        db.flush()

    @staticmethod
    def delete(db: Session, site: Site) -> None:
        db.delete(site)
        db.flush()
