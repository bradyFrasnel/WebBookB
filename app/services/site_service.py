from datetime import datetime, timezone
import ipaddress
from urllib.parse import urlparse
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflitMetierError,
    RessourceIntrouvableError,
)
from app.models import Site
from app.repositories.categorie_repository import CategorieRepository
from app.repositories.historique_repository import HistoriqueRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.site import SiteCreate, SiteUpdate


def _is_local_or_ip_hostname(hostname: str) -> bool:
    h = hostname.lower()
    if (
        h == "localhost"
        or h.endswith(".local")
        or h.endswith(".localhost")
        or h.endswith(".test")
        or h.endswith(".internal")
        or "." not in h
    ):
        return True
    try:
        ipaddress.ip_address(h)
        return True
    except ValueError:
        return False


def build_favicon_url(site_url: str) -> str | None:
    """Construit automatiquement l'URL du favicon à partir du domaine public du site."""
    parsed = urlparse(site_url)
    hostname = parsed.hostname
    if not hostname or _is_local_or_ip_hostname(hostname):
        return None
    return f"https://www.google.com/s2/favicons?domain={hostname}&sz=64"


class SiteService:
    @staticmethod
    def list_sites(
        db: Session,
        id_utilisateur: uuid.UUID,
        q: str | None = None,
        id_categorie: uuid.UUID | None = None,
        favori: bool | None = None,
    ) -> list[Site]:
        if id_categorie is not None:
            categorie = CategorieRepository.get_by_id(
                db, id_categorie, id_utilisateur
            )
            if categorie is None:
                raise RessourceIntrouvableError("Catégorie introuvable.")

        return SiteRepository.get_all(
            db=db,
            id_utilisateur=id_utilisateur,
            q=q,
            id_categorie=id_categorie,
            favori=favori,
        )

    @staticmethod
    def list_recent_sites(
        db: Session,
        id_utilisateur: uuid.UUID,
        limit: int = 10,
    ) -> list[Site]:
        return SiteRepository.get_recently_visited(
            db=db,
            id_utilisateur=id_utilisateur,
            limit=limit,
        )

    @staticmethod
    def get_site(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_site: uuid.UUID,
    ) -> Site:
        site = SiteRepository.get_by_id(db, id_site, id_utilisateur)
        if site is None:
            raise RessourceIntrouvableError("Site introuvable.")
        return site

    @staticmethod
    def create_site(
        db: Session,
        id_utilisateur: uuid.UUID,
        data: SiteCreate,
    ) -> Site:
        categorie = CategorieRepository.get_by_id(
            db, data.id_categorie, id_utilisateur
        )
        if categorie is None:
            raise RessourceIntrouvableError(
                "La catégorie sélectionnée est introuvable."
            )

        existant = SiteRepository.get_by_url_ci(db, id_utilisateur, data.url)
        if existant is not None:
            raise ConflitMetierError(
                "Ce site (URL) est déjà enregistré dans votre espace."
            )

        icone_url = data.icone_url or build_favicon_url(data.url)

        try:
            site = SiteRepository.create(
                db=db,
                id_utilisateur=id_utilisateur,
                id_categorie=data.id_categorie,
                nom=data.nom,
                url=data.url,
                icone_url=icone_url,
                favori=data.favori,
                note_personnelle=data.note_personnelle,
            )
            db.commit()
            return SiteService.get_site(db, id_utilisateur, site.id_site)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def update_site(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_site: uuid.UUID,
        data: SiteUpdate,
    ) -> Site:
        site = SiteRepository.get_by_id(db, id_site, id_utilisateur)
        if site is None:
            raise RessourceIntrouvableError("Site introuvable.")

        if (
            data.id_categorie is not None
            and data.id_categorie != site.id_categorie
        ):
            categorie = CategorieRepository.get_by_id(
                db, data.id_categorie, id_utilisateur
            )
            if categorie is None:
                raise RessourceIntrouvableError(
                    "La catégorie sélectionnée est introuvable."
                )
            site.id_categorie = data.id_categorie

        url_modifiee = False
        if data.url is not None and data.url != site.url:
            existant = SiteRepository.get_by_url_ci(
                db, id_utilisateur, data.url
            )
            if existant is not None and existant.id_site != site.id_site:
                raise ConflitMetierError(
                    "Un autre site utilise déjà cette adresse URL."
                )
            site.url = data.url
            url_modifiee = True

        if data.nom is not None:
            site.nom = data.nom

        if "icone_url" in data.model_fields_set:
            site.icone_url = data.icone_url or build_favicon_url(site.url)
        elif url_modifiee:
            site.icone_url = build_favicon_url(site.url)

        if data.favori is not None:
            site.favori = data.favori

        if "note_personnelle" in data.model_fields_set:
            site.note_personnelle = data.note_personnelle

        try:
            db.flush()
            db.commit()
            return SiteService.get_site(db, id_utilisateur, site.id_site)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def toggle_favori(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_site: uuid.UUID,
    ) -> Site:
        site = SiteRepository.get_by_id(db, id_site, id_utilisateur)
        if site is None:
            raise RessourceIntrouvableError("Site introuvable.")

        try:
            site.favori = not site.favori
            db.flush()
            db.commit()
            return SiteService.get_site(db, id_utilisateur, site.id_site)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def record_visit(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_site: uuid.UUID,
    ) -> Site:
        site = SiteRepository.get_by_id(db, id_site, id_utilisateur)
        if site is None:
            raise RessourceIntrouvableError("Site introuvable.")

        try:
            site.nombre_consultations = (site.nombre_consultations or 0) + 1
            site.derniere_consultation = datetime.now(timezone.utc)
            HistoriqueRepository.create(
                db=db,
                id_utilisateur=id_utilisateur,
                id_site=id_site,
            )
            db.flush()
            db.commit()
            return SiteService.get_site(db, id_utilisateur, site.id_site)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_site(
        db: Session,
        id_utilisateur: uuid.UUID,
        id_site: uuid.UUID,
    ) -> None:
        site = SiteRepository.get_by_id(db, id_site, id_utilisateur)
        if site is None:
            raise RessourceIntrouvableError("Site introuvable.")

        try:
            SiteRepository.delete(db, site)
            db.commit()
        except Exception:
            db.rollback()
            raise
