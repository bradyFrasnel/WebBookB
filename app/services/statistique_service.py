import uuid

from sqlalchemy.orm import Session

from app.repositories.categorie_repository import CategorieRepository
from app.repositories.historique_repository import HistoriqueRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.statistique import (
    RepartitionCategorieItem,
    StatistiquesResponse,
)


class StatistiqueService:
    @staticmethod
    def get_statistiques(
        db: Session,
        id_utilisateur: uuid.UUID,
    ) -> StatistiquesResponse:
        total_sites = SiteRepository.count_all(db, id_utilisateur)
        total_favoris = SiteRepository.count_favoris(db, id_utilisateur)
        total_notes = NoteRepository.count_all(db, id_utilisateur)
        total_consultations = HistoriqueRepository.count_all(
            db, id_utilisateur
        )
        categories_avec_comptage = (
            CategorieRepository.get_all_with_site_count(db, id_utilisateur)
        )
        total_categories = len(categories_avec_comptage)

        repartition: list[RepartitionCategorieItem] = []
        for cat, count in categories_avec_comptage:
            pourcentage = (
                round((count / total_sites) * 100, 2)
                if total_sites > 0
                else 0.0
            )
            repartition.append(
                RepartitionCategorieItem(
                    id_categorie=cat.id_categorie,
                    nom=cat.nom,
                    est_personnalisee=cat.est_personnalisee,
                    nombre_sites=count,
                    pourcentage=pourcentage,
                )
            )

        return StatistiquesResponse(
            total_sites=total_sites,
            total_categories=total_categories,
            total_favoris=total_favoris,
            total_notes=total_notes,
            total_consultations=total_consultations,
            repartition_par_categorie=repartition,
        )
