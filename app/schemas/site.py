from datetime import datetime
from urllib.parse import urlparse
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _valider_et_normaliser_url(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("L'URL ne peut pas être vide.")

    if "://" not in cleaned:
        cleaned = f"https://{cleaned}"

    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(
            "L'URL doit être une adresse HTTP ou HTTPS valide (ex: https://exemple.com)."
        )
    if "." not in parsed.netloc and parsed.hostname != "localhost":
        raise ValueError("Le domaine de l'URL est invalide.")

    return cleaned


class CategorieMiniResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_categorie: uuid.UUID
    nom: str
    est_personnalisee: bool


class SiteCreate(BaseModel):
    nom: str = Field(
        min_length=1,
        max_length=150,
        description="Nom de la plateforme",
    )
    url: str = Field(
        min_length=1,
        max_length=2048,
        description="Adresse URL du site",
    )
    id_categorie: uuid.UUID = Field(
        description="Identifiant de la catégorie associée",
    )
    icone_url: str | None = Field(
        default=None,
        max_length=2048,
        description="URL d'une icône personnalisée (optionnel, générée automatiquement sinon)",
    )
    favori: bool = Field(
        default=False,
        description="Indique si le site est marqué comme favori",
    )
    note_personnelle: str | None = Field(
        default=None,
        max_length=5000,
        description="Note rapide ou mémo personnel attaché à ce site",
    )

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Le nom du site ne peut pas être vide.")
        return cleaned

    @field_validator("url")
    @classmethod
    def valider_url(cls, value: str) -> str:
        return _valider_et_normaliser_url(value)

    @field_validator("icone_url")
    @classmethod
    def valider_icone_url(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        return _valider_et_normaliser_url(value)

    @field_validator("note_personnelle")
    @classmethod
    def nettoyer_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class SiteUpdate(BaseModel):
    nom: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
        description="Nouveau nom de la plateforme",
    )
    url: str | None = Field(
        default=None,
        min_length=1,
        max_length=2048,
        description="Nouvelle adresse URL du site",
    )
    id_categorie: uuid.UUID | None = Field(
        default=None,
        description="Nouvel identifiant de catégorie",
    )
    icone_url: str | None = Field(
        default=None,
        max_length=2048,
        description="Nouvelle URL d'icône personnalisée",
    )
    favori: bool | None = Field(
        default=None,
        description="Statut favori",
    )
    note_personnelle: str | None = Field(
        default=None,
        max_length=5000,
        description="Note rapide ou mémo personnel attaché à ce site",
    )

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Le nom du site ne peut pas être vide.")
        return cleaned

    @field_validator("url")
    @classmethod
    def valider_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _valider_et_normaliser_url(value)

    @field_validator("icone_url")
    @classmethod
    def valider_icone_url(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        return _valider_et_normaliser_url(value)

    @field_validator("note_personnelle")
    @classmethod
    def nettoyer_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class SiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_site: uuid.UUID
    id_categorie: uuid.UUID
    nom: str
    url: str
    icone_url: str | None
    favori: bool
    note_personnelle: str | None = None
    derniere_consultation: datetime | None = None
    nombre_consultations: int = 0
    date_creation: datetime
    categorie: CategorieMiniResponse | None = None
