from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailDejaUtiliseError,
    IdentifiantsInvalidesError,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models import Utilisateur
from app.repositories.categorie_repository import CategorieRepository
from app.repositories.utilisateur_repository import UtilisateurRepository
from app.schemas.auth import TokenResponse
from app.schemas.utilisateur import UtilisateurCreate

CATEGORIES_PREDEFINIES: list[str] = [
    "Professionnel",
    "Divertissement",
    "Réseaux sociaux",
    "Éducation",
    "Développement",
    "Stockage",
    "Finance",
    "Communication",
    "Autres",
]


class AuthService:
    @staticmethod
    def register(db: Session, data: UtilisateurCreate) -> Utilisateur:
        email_normalise = data.email.strip().lower()

        existant = UtilisateurRepository.get_by_email(db, email_normalise)
        if existant is not None:
            raise EmailDejaUtiliseError(
                "Un compte existe déjà avec cette adresse email."
            )

        nom_utilisateur = data.nom_utilisateur or email_normalise.split("@")[0]
        mot_de_passe_hash = hash_password(data.mot_de_passe)

        try:
            utilisateur = UtilisateurRepository.create(
                db=db,
                email=email_normalise,
                nom_utilisateur=nom_utilisateur,
                mot_de_passe_hash=mot_de_passe_hash,
            )
            CategorieRepository.create_many(
                db=db,
                id_utilisateur=utilisateur.id_utilisateur,
                noms=CATEGORIES_PREDEFINIES,
                est_personnalisee=False,
            )
            db.commit()
            db.refresh(utilisateur)
            return utilisateur
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def login(db: Session, email: str, mot_de_passe: str) -> TokenResponse:
        email_normalise = email.strip().lower()
        utilisateur = UtilisateurRepository.get_by_email(db, email_normalise)

        if utilisateur is None or not verify_password(
            mot_de_passe,
            utilisateur.mot_de_passe_hash,
        ):
            raise IdentifiantsInvalidesError(
                "Email ou mot de passe incorrect."
            )

        access_token = create_access_token(
            subject=str(utilisateur.id_utilisateur)
        )
        return TokenResponse(access_token=access_token, token_type="bearer")
