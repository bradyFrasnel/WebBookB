from datetime import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class HistoriqueConsultation(Base):
    __tablename__ = "historique_consultation"

    id_consultation: Mapped[uuid.UUID] = mapped_column(
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

    id_site: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("site.id_site", ondelete="CASCADE"),
        nullable=False,
    )

    date_consultation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    utilisateur = relationship(
        "Utilisateur",
        back_populates="consultations",
    )

    site = relationship(
        "Site",
        back_populates="consultations",
    )
