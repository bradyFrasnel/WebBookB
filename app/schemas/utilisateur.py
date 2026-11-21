from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UtilisateurCreate(BaseModel):
    email: EmailStr
    nom_utilisateur: str | None = Field(
        default=None,
        max_length=100,
        description="Nom ou pseudo d'affichage (optionnel)",
    )
    mot_de_passe: str = Field(
        min_length=8,
        max_length=128,
        description="Mot de passe d'au moins 8 caractères",
    )

    @field_validator("nom_utilisateur")
    @classmethod
    def nettoyer_nom_utilisateur(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class UtilisateurUpdate(BaseModel):
    email: EmailStr | None = Field(
        default=None,
        description="Nouvelle adresse email",
    )
    nom_utilisateur: str | None = Field(
        default=None,
        max_length=100,
        description="Nouveau nom ou pseudo d'affichage",
    )

    @field_validator("nom_utilisateur")
    @classmethod
    def nettoyer_nom_utilisateur(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class MotDePasseUpdate(BaseModel):
    ancien_mot_de_passe: str = Field(
        min_length=1,
        description="Mot de passe actuel",
    )
    nouveau_mot_de_passe: str = Field(
        min_length=8,
        max_length=128,
        description="Nouveau mot de passe (au moins 8 caractères)",
    )


class UtilisateurResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_utilisateur: uuid.UUID
    email: EmailStr
    nom_utilisateur: str | None = None
    date_creation: datetime
