import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflitMetierError,
    RessourceIntrouvableError,
)
from app.models import Site, Utilisateur
from app.schemas.site import SiteCreate, SiteUpdate
from app.services.site_service import SiteService


class SiteController:
    @staticmethod
    def list_sites(
        db: Session,
        current_user: Utilisateur,
        q: str | None = None,
        id_categorie: uuid.UUID | None = None,
        favori: bool | None = None,
    ) -> list[Site]:
        try:
            return SiteService.list_sites(
                db=db,
                id_utilisateur=current_user.id_utilisateur,
                q=q,
                id_categorie=id_categorie,
                favori=favori,
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def list_recent_sites(
        db: Session,
        current_user: Utilisateur,
        limit: int = 10,
    ) -> list[Site]:
        return SiteService.list_recent_sites(
            db=db,
            id_utilisateur=current_user.id_utilisateur,
            limit=limit,
        )

    @staticmethod
    def get_site(
        db: Session,
        current_user: Utilisateur,
        id_site: uuid.UUID,
    ) -> Site:
        try:
            return SiteService.get_site(
                db, current_user.id_utilisateur, id_site
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def create_site(
        db: Session,
        current_user: Utilisateur,
        data: SiteCreate,
    ) -> Site:
        try:
            return SiteService.create_site(
                db, current_user.id_utilisateur, data
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc
        except ConflitMetierError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=exc.message,
            ) from exc

    @staticmethod
    def update_site(
        db: Session,
        current_user: Utilisateur,
        id_site: uuid.UUID,
        data: SiteUpdate,
    ) -> Site:
        try:
            return SiteService.update_site(
                db, current_user.id_utilisateur, id_site, data
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc
        except ConflitMetierError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=exc.message,
            ) from exc

    @staticmethod
    def toggle_favori(
        db: Session,
        current_user: Utilisateur,
        id_site: uuid.UUID,
    ) -> Site:
        try:
            return SiteService.toggle_favori(
                db, current_user.id_utilisateur, id_site
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def record_visit(
        db: Session,
        current_user: Utilisateur,
        id_site: uuid.UUID,
    ) -> Site:
        try:
            return SiteService.record_visit(
                db, current_user.id_utilisateur, id_site
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def delete_site(
        db: Session,
        current_user: Utilisateur,
        id_site: uuid.UUID,
    ) -> None:
        try:
            SiteService.delete_site(db, current_user.id_utilisateur, id_site)
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc
