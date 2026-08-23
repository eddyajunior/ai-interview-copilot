from enum import Enum

from pydantic import BaseModel, ConfigDict


class EvidenceSource(str, Enum):
    PROFESSIONAL_SUMMARY = "professional_summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATION = "certification"
    SKILL_SECTION = "skill_section"
    JOB_DESCRIPTION = "job_description"
    OTHER = "other"


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    source: EvidenceSource

    source_reference: str | None
    page: int | None