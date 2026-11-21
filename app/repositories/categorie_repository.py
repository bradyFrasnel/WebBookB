import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models import Categorie, Site


class CategorieRepository:
    @staticmethod
    def create_many(
        db: Session,
        id_utilisateur: uuid.UUID,
        noms: list[str],
        est_personnalisee: bool = False,
    ) -> list[Categorie]:
        categories = [
            Categorie(
                id_utilisateur=id_utilisateur,
                nom=nom,
                est_personnalisee=est_personnalisee,
            )
            for nom in noms
        ]
        db.add_all(categories)
        db.flush()
        return categories

    @staticmethod
    def get_all_with_site_count(
        db: Session,
        id_utilisateur: uuid.UUID,
    ) -> list[tuple[Categorie, int]]:
        stmt = (
            select(
                Categorie,
                func.count(Site.id_site).label("nombre_sites"),
            )
            .outerjoin(
                Site,
                (Site.id_categorie == Categorie.id_categorie)
                & (Site.id_utilisateur == Categorie.id_utilisateur),
            )
            .where(Categorie.id_utilisateur == id_utilisateur)
            .group_by(Categorie.id_categorie)
            .order_by(Categorie.est_personnalisee.asc(), Categorie.nom.asc())
        )
        rows = db.execute(stmt).all()
        return [(row[0], int(row[1])) for row in rows]

    @staticmethod
    def get_by_id(
        db: Session,
        id_categorie: uuid.UUID,
        id_utilisateur: uuid.UUID,
    ) -> Categorie | None:
        stmt = select(Categorie).where(
            Categorie.id_categorie == id_categorie,
            Categorie.id_utilisateur == id_utilisateur,
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_by_nom_ci(
        db: Session,
        id_utilisateur: uuid.UUID,
        nom: str,
    ) -> Categorie | None:
        stmt = select(Categorie).where(
            Categorie.id_utilisateur == id_utilisateur,
            func.lower(Categorie.nom) == nom.lower(),
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def count_sites(
        db: Session,
        id_categorie: uuid.UUID,
        id_utilisateur: uuid.UUID,
    ) -> int:
        stmt = select(func.count(Site.id_site)).where(
            Site.id_categorie == id_categorie,
            Site.id_utilisateur == id_utilisateur,
        )
        return int(db.execute(stmt).scalar_one())

    @staticmethod
    def create(
        db: Session,
        id_utilisateur: uuid.UUID,
        nom: str,
        est_personnalisee: bool = True,
    ) -> Categorie:
        categorie = Categorie(
            id_utilisateur=id_utilisateur,
            nom=nom,
            est_personnalisee=est_personnalisee,
        )
        db.add(categorie)
        db.flush()
        return categorie

    @staticmethod
    def update_nom(
        db: Session,
        categorie: Categorie,
        nom: str,
    ) -> Categorie:
        categorie.nom = nom
        db.flush()
        return categorie

    @staticmethod
    def reassign_sites(
        db: Session,
        id_utilisateur: uuid.UUID,
        old_categorie_id: uuid.UUID,
        new_categorie_id: uuid.UUID,
    ) -> None:
        stmt = (
            update(Site)
            .where(
                Site.id_utilisateur == id_utilisateur,
                Site.id_categorie == old_categorie_id,
            )
            .values(id_categorie=new_categorie_id)
        )
        db.execute(stmt)
        db.flush()

    @staticmethod
    def delete(db: Session, categorie: Categorie) -> None:
        db.delete(categorie)
        db.flush()
