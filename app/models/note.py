from datetime import datetime
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Note(Base):
    __tablename__ = "note"

    id_note: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    id_utilisateur: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("utilisateur.id_utilisateur", ondelete="CASCADE"),
        nullable=False,
    )

    id_site: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("site.id_site", ondelete="SET NULL"),
        nullable=True,
    )

    titre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    contenu: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    epingle: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    utilisateur = relationship(
        "Utilisateur",
        back_populates="notes",
    )

    site = relationship(
        "Site",
        back_populates="notes",
    )
