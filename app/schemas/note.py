from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SiteMiniResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_site: uuid.UUID
    nom: str
    url: str
    icone_url: str | None = None


class NoteCreate(BaseModel):
    titre: str = Field(
        min_length=1,
        max_length=200,
        description="Titre de la note personnelle",
    )
    contenu: str = Field(
        min_length=1,
        max_length=20000,
        description="Contenu détaillé de la note",
    )
    id_site: uuid.UUID | None = Field(
        default=None,
        description="Identifiant du site associé (optionnel)",
    )
    epingle: bool = Field(
        default=False,
        description="Indique si la note est épinglée en haut de liste",
    )

    @field_validator("titre")
    @classmethod
    def nettoyer_titre(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Le titre de la note ne peut pas être vide.")
        return cleaned

    @field_validator("contenu")
    @classmethod
    def nettoyer_contenu(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Le contenu de la note ne peut pas être vide.")
        return cleaned


class NoteUpdate(BaseModel):
    titre: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Nouveau titre de la note",
    )
    contenu: str | None = Field(
        default=None,
        min_length=1,
        max_length=20000,
        description="Nouveau contenu de la note",
    )
    id_site: uuid.UUID | None = Field(
        default=None,
        description="Nouvel identifiant de site associé (null pour détacher)",
    )
    epingle: bool | None = Field(
        default=None,
        description="Statut épinglé",
    )

    @field_validator("titre")
    @classmethod
    def nettoyer_titre(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Le titre de la note ne peut pas être vide.")
        return cleaned

    @field_validator("contenu")
    @classmethod
    def nettoyer_contenu(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Le contenu de la note ne peut pas être vide.")
        return cleaned


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_note: uuid.UUID
    id_site: uuid.UUID | None = None
    titre: str
    contenu: str
    epingle: bool
    date_creation: datetime
    date_modification: datetime
    site: SiteMiniResponse | None = None
