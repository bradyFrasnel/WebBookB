from datetime import datetime
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Site(Base):
    __tablename__ = "site"

    __table_args__ = (
        ForeignKeyConstraint(
            ["id_categorie", "id_utilisateur"],
            ["categorie.id_categorie", "categorie.id_utilisateur"],
            name="fk_site_categorie_utilisateur",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "id_utilisateur",
            "url",
            name="uq_site_utilisateur_url",
        ),
    )

    id_site: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    id_utilisateur: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("utilisateur.id_utilisateur", ondelete="CASCADE"),
        nullable=False,
    )

    id_categorie: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    nom: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    icone_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    favori: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    note_personnelle: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    derniere_consultation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    nombre_consultations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    utilisateur = relationship(
        "Utilisateur",
        back_populates="sites",
        overlaps="categorie,sites",
    )

    categorie = relationship(
        "Categorie",
        back_populates="sites",
        overlaps="utilisateur,sites",
    )

    notes = relationship(
        "Note",
        back_populates="site",
        passive_deletes=True,
    )

    consultations = relationship(
        "HistoriqueConsultation",
        back_populates="site",
        passive_deletes=True,
    )
