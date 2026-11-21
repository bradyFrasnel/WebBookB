from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategorieBase(BaseModel):
    nom: str = Field(
        min_length=1,
        max_length=100,
        description="Nom de la catégorie",
    )

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Le nom de la catégorie ne peut pas être vide.")
        return cleaned


class CategorieCreate(CategorieBase):
    pass


class CategorieUpdate(CategorieBase):
    pass


class CategorieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_categorie: uuid.UUID
    nom: str
    est_personnalisee: bool
    date_creation: datetime
    nombre_sites: int = 0
