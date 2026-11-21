import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflitMetierError,
    RessourceIntrouvableError,
    ValidationMetierError,
)
from app.models import Categorie
from app.repositories.categorie_repository import CategorieRepository
from app.schemas.categorie import (
    CategorieCreate,
    CategorieResponse,
    CategorieUpdate,
)


def _to_response(categorie: Categorie, nombre_sites: int) -> CategorieResponse:
    return CategorieResponse(
        id_categorie=categorie.id_categorie,
        nom=categorie.nom,
        est_personnalisee=categorie.est_personnalisee,
        date_creation=categorie.date_creation,
        nombre_sites=nombre_sites,
    )


class CategorieService:
    @staticmethod
    def list_categories(
        db: Session,
        id_utilisateur: uuid.UUID,
    ) -> list[CategorieResponse]:
        rows = CategorieRepository.get_all_with_site_count(db, id_utilisateur)
        return [_to_response(cat, count) for cat, count in rows]

    @staticmethod
    def get_categorie(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_categorie: uuid.UUID,
    ) -> CategorieResponse:
        categorie = CategorieRepository.get_by_id(
            db, id_categorie, id_utilisateur
        )
        if categorie is None:
            raise RessourceIntrouvableError("Catégorie introuvable.")

        nombre_sites = CategorieRepository.count_sites(
            db, id_categorie, id_utilisateur
        )
        return _to_response(categorie, nombre_sites)

    @staticmethod
    def create_categorie(
        db: Session,
        id_utilisateur: uuid.UUID,
        data: CategorieCreate,
    ) -> CategorieResponse:
        existante = CategorieRepository.get_by_nom_ci(
            db, id_utilisateur, data.nom
        )
        if existante is not None:
            raise ConflitMetierError(
                f"Une catégorie nommée '{data.nom}' existe déjà."
            )

        try:
            categorie = CategorieRepository.create(
                db=db,
                id_utilisateur=id_utilisateur,
                nom=data.nom,
                est_personnalisee=True,
            )
            db.commit()
            db.refresh(categorie)
            return _to_response(categorie, 0)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def update_categorie(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_categorie: uuid.UUID,
        data: CategorieUpdate,
    ) -> CategorieResponse:
        categorie = CategorieRepository.get_by_id(
            db, id_categorie, id_utilisateur
        )
        if categorie is None:
            raise RessourceIntrouvableError("Catégorie introuvable.")

        existante = CategorieRepository.get_by_nom_ci(
            db, id_utilisateur, data.nom
        )
        if (
            existante is not None
            and existante.id_categorie != categorie.id_categorie
        ):
            raise ConflitMetierError(
                f"Une catégorie nommée '{data.nom}' existe déjà."
            )

        try:
            CategorieRepository.update_nom(db, categorie, data.nom)
            db.commit()
            db.refresh(categorie)
            nombre_sites = CategorieRepository.count_sites(
                db, id_categorie, id_utilisateur
            )
            return _to_response(categorie, nombre_sites)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_categorie(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_categorie: uuid.UUID,
        nouvelle_categorie_id: uuid.UUID | None = None,
    ) -> None:
        categorie = CategorieRepository.get_by_id(
            db, id_categorie, id_utilisateur
        )
        if categorie is None:
            raise RessourceIntrouvableError("Catégorie introuvable.")

        nombre_sites = CategorieRepository.count_sites(
            db, id_categorie, id_utilisateur
        )

        if nombre_sites > 0:
            if nouvelle_categorie_id is None:
                raise ConflitMetierError(
                    f"Impossible de supprimer cette catégorie car elle contient encore {nombre_sites} site(s). "
                    "Veuillez définir une nouvelle catégorie via le paramètre 'nouvelle_categorie_id'."
                )
            if nouvelle_categorie_id == id_categorie:
                raise ValidationMetierError(
                    "La nouvelle catégorie doit être différente de la catégorie à supprimer."
                )
            categorie_cible = CategorieRepository.get_by_id(
                db, nouvelle_categorie_id, id_utilisateur
            )
            if categorie_cible is None:
                raise RessourceIntrouvableError(
                    "La catégorie de remplacement est introuvable."
                )

        try:
            if nombre_sites > 0 and nouvelle_categorie_id is not None:
                CategorieRepository.reassign_sites(
                    db=db,
                    id_utilisateur=id_utilisateur,
                    old_categorie_id=id_categorie,
                    new_categorie_id=nouvelle_categorie_id,
                )
            CategorieRepository.delete(db, categorie)
            db.commit()
        except Exception:
            db.rollback()
            raise
