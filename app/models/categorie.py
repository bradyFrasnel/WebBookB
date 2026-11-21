
from datetime import datetime
import uuid

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Categorie(Base):
    __tablename__ = "categorie"

    __table_args__ = (
        UniqueConstraint(
            "id_categorie",
            "id_utilisateur",
            name="uq_categorie_utilisateur"
        ),
        UniqueConstraint(
            "id_utilisateur",
            "nom",
            name="uq_nom_categorie_utilisateur"
        ),
    )

    id_categorie: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    id_utilisateur: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("utilisateur.id_utilisateur", ondelete="CASCADE"),
        nullable=False
    )

    nom: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    est_personnalisee: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    utilisateur = relationship(
        "Utilisateur",
        back_populates="categories"
    )

    sites = relationship(
        "Site",
        back_populates="categorie",
        overlaps="utilisateur,sites"
    )
