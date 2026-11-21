from datetime import datetime
import uuid

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id_utilisateur: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    nom_utilisateur: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    mot_de_passe_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    categories = relationship(
        "Categorie",
        back_populates="utilisateur",
        passive_deletes=True,
    )

    sites = relationship(
        "Site",
        back_populates="utilisateur",
        overlaps="categorie,sites",
        passive_deletes=True,
    )

    notes = relationship(
        "Note",
        back_populates="utilisateur",
        passive_deletes=True,
    )

    consultations = relationship(
        "HistoriqueConsultation",
        back_populates="utilisateur",
        passive_deletes=True,
    )
