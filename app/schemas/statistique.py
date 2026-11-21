import uuid

from pydantic import BaseModel


class RepartitionCategorieItem(BaseModel):
    id_categorie: uuid.UUID
    nom: str
    est_personnalisee: bool
    nombre_sites: int
    pourcentage: float


class StatistiquesResponse(BaseModel):
    total_sites: int
    total_categories: int
    total_favoris: int
    total_notes: int = 0
    total_consultations: int = 0
    repartition_par_categorie: list[RepartitionCategorieItem]
