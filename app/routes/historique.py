import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers.historique_controller import HistoriqueController
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models import Utilisateur
from app.schemas.historique import HistoriqueConsultationResponse

router = APIRouter(
    prefix="/api/historique",
    tags=["Historique des consultations"],
)


@router.get(
    "",
    response_model=list[HistoriqueConsultationResponse],
    summary="Consulter l'historique détaillé des visites de sites",
)
def list_historique(
    id_site: uuid.UUID | None = Query(
        default=None,
        description="Filtrer l'historique pour un site précis",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Nombre maximum d'entrées d'historique à retourner",
    ),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return HistoriqueController.list_historique(
        db=db,
        current_user=current_user,
        id_site=id_site,
        limit=limit,
    )


@router.delete(
    "/{id_consultation}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une entrée précise de l'historique",
)
def delete_consultation(
    id_consultation: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    HistoriqueController.delete_consultation(
        db=db,
        current_user=current_user,
        id_consultation=id_consultation,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Effacer tout l'historique de consultation de l'utilisateur",
)
def clear_historique(
    reinitialiser_compteurs: bool = Query(
        default=True,
        description="Réinitialiser également les compteurs et dates de dernière consultation sur les sites",
    ),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    HistoriqueController.clear_historique(
        db=db,
        current_user=current_user,
        reinitialiser_compteurs=reinitialiser_compteurs,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
