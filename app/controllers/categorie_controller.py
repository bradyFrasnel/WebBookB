import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflitMetierError,
    RessourceIntrouvableError,
    ValidationMetierError,
)
from app.models import Utilisateur
from app.schemas.categorie import (
    CategorieCreate,
    CategorieResponse,
    CategorieUpdate,
)
from app.services.categorie_service import CategorieService


class CategorieController:
    @staticmethod
    def list_categories(
        db: Session,
        current_user: Utilisateur,
    ) -> list[CategorieResponse]:
        return CategorieService.list_categories(db, current_user.id_utilisateur)

    @staticmethod
    def get_categorie(
        db: Session,
        current_user: Utilisateur,
        id_categorie: uuid.UUID,
    ) -> CategorieResponse:
        try:
            return CategorieService.get_categorie(
                db, current_user.id_utilisateur, id_categorie
            )
        except RessourceIntrouvableError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=exc.message,
            ) from exc

    @staticmethod
    def create_categorie(
        db: Session,
        current_user: Utilisateur,
        data: CategorieCreate,
    ) -> CategorieResponse:
        try:
            return CategorieService.create_categorie(
                db, current_user.id_utilisateur, data
            )
        except ConflitMetierError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=exc.message,
            ) from exc

    @staticmethod
    def update_categorie(
        db: Session,
        current_user: Utilisateur,
        id_categorie: uuid.UUID,
        data: CategorieUpdate,
    ) -> CategorieResponse:
        try:
            return CategorieService.update_categorie(
                db, current_user.id_utilisateur, id_categorie, data
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
    def delete_categorie(
        db: Session,
        current_user: Utilisateur,
        id_categorie: uuid.UUID,
        nouvelle_categorie_id: uuid.UUID | None = None,
    ) -> None:
        try:
            CategorieService.delete_categorie(
                db=db,
                id_utilisateur=current_user.id_utilisateur,
                id_categorie=id_categorie,
                nouvelle_categorie_id=nouvelle_categorie_id,
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
        except ValidationMetierError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exc.message,
            ) from exc
