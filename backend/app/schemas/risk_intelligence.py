from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.schemas.evidence import Evidence


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskCategory(str, Enum):
    EVIDENCE_GAP = "evidence_gap"
    LIMITED_EVIDENCE = "limited_evidence"
    VALIDATION_REQUIRED = "validation_required"
    OTHER = "other"


class RiskAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    competency: str
    title: str
    category: RiskCategory
    level: RiskLevel
    description: str
    evidence: list[Evidence]
    validation_question: str | None


class RiskAssessmentSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risks: list[RiskAssessment]