from sqlalchemy.orm import Session

from app.core.audit_logger import log_security_event, mask_email
from app.core.exceptions import (
    EmailDejaUtiliseError,
    IdentifiantsInvalidesError,
    RessourceIntrouvableError,
)
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    hash_password,
    is_reset_token_still_unused,
    verify_password,
)
from app.models import Utilisateur
from app.repositories.categorie_repository import CategorieRepository
from app.repositories.utilisateur_repository import UtilisateurRepository
from app.schemas.auth import TokenResponse
from app.schemas.utilisateur import UtilisateurCreate
from app.services.email_service import EmailService

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
            log_security_event(
                "AUTH_REGISTER_DUPLICATE", email=mask_email(email_normalise)
            )
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
            log_security_event(
                "AUTH_REGISTER_SUCCESS",
                user_id=utilisateur.id_utilisateur,
                email=mask_email(email_normalise),
            )
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
            log_security_event(
                "AUTH_LOGIN_FAILED", email=mask_email(email_normalise)
            )
            raise IdentifiantsInvalidesError(
                "Email ou mot de passe incorrect."
            )

        access_token = create_access_token(
            subject=str(utilisateur.id_utilisateur)
        )
        log_security_event(
            "AUTH_LOGIN_SUCCESS",
            user_id=utilisateur.id_utilisateur,
            email=mask_email(email_normalise),
        )
        return TokenResponse(access_token=access_token, token_type="bearer")

    @staticmethod
    def demander_reinitialisation_mot_de_passe(db: Session, email: str) -> str:
        email_normalise = email.strip().lower()
        utilisateur = UtilisateurRepository.get_by_email(db, email_normalise)
        if utilisateur is None:
            log_security_event(
                "AUTH_PASSWORD_RESET_UNKNOWN_EMAIL",
                email=mask_email(email_normalise),
            )
            raise RessourceIntrouvableError(
                "Aucun compte n'est rattaché à cette adresse mail."
            )
        token = create_password_reset_token(
            utilisateur.email, utilisateur.mot_de_passe_hash
        )
        EmailService.send_password_reset_email(utilisateur.email, token)
        log_security_event(
            "AUTH_PASSWORD_RESET_SENT",
            user_id=utilisateur.id_utilisateur,
            email=mask_email(utilisateur.email),
        )
        return utilisateur.email

    @staticmethod
    def reinitialiser_mot_de_passe(
        db: Session, token: str, nouveau_mot_de_passe: str
    ) -> None:
        if len(nouveau_mot_de_passe) < 8 or len(nouveau_mot_de_passe) > 128:
            raise ValueError(
                "Le nouveau mot de passe doit comporter entre 8 et 128 caractères."
            )

        email, token_pwd_fp = decode_password_reset_token(token)
        utilisateur = UtilisateurRepository.get_by_email(db, email)
        if utilisateur is None:
            raise ValueError("Compte utilisateur introuvable.")

        if not is_reset_token_still_unused(
            token_pwd_fp, utilisateur.mot_de_passe_hash
        ):
            log_security_event(
                "AUTH_PASSWORD_RESET_REPLAY_BLOCKED",
                user_id=utilisateur.id_utilisateur,
            )
            raise ValueError(
                "Ce lien de réinitialisation a déjà été utilisé ou a expiré."
            )

        nouveau_hash = hash_password(nouveau_mot_de_passe)
        UtilisateurRepository.update_password(db, utilisateur, nouveau_hash)
        db.commit()
        log_security_event(
            "AUTH_PASSWORD_RESET_SUCCESS",
            user_id=utilisateur.id_utilisateur,
            email=mask_email(utilisateur.email),
        )
