from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict

from app.schemas.note import SiteMiniResponse


class HistoriqueConsultationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_consultation: uuid.UUID
    id_site: uuid.UUID
    date_consultation: datetime
    site: SiteMiniResponse | None = None
