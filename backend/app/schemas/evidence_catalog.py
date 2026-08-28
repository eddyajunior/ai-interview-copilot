from pydantic import BaseModel, ConfigDict

from app.schemas.evidence import Evidence


class EvidenceCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidences: list[Evidence]