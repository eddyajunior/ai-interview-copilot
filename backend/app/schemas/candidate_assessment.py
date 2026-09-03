from enum import Enum
from typing import List
from pydantic import BaseModel, Field

from app.schemas.evidence import Evidence

from app.schemas.interview_intelligence import (
    InterviewQuestion,
)
from app.schemas.risk_intelligence import (
    RiskAssessment,
)

class SkillType(str, Enum):
    HARD_SKILL = "hard_skill"
    SOFT_SKILL = "soft_skill"
    TECHNOLOGY = "technology"


# class RiskLevel(str, Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SkillAssessment(BaseModel):
    name: str
    type: SkillType

    score: int = Field(
        ge=1,
        le=5,
        description="Nível de evidência encontrado no currículo em relação à vaga"
    )

    evidence: List[Evidence] = Field(default_factory=list)

    justification: str

    confidence: ConfidenceLevel

    status: str


    # class RiskAssessment(BaseModel):
    #     title: str
    #     level: RiskLevel
    #     description: str
    #     evidence: List[Evidence] = Field(default_factory=list)
    #     validation_question: str | None = None


class Recommendation(BaseModel):
    short_term: str
    medium_term: str
    long_term: str


class CandidateAssessment(BaseModel):
    candidate_name: str | None = None
    job_title: str

    summary: str

    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)

    hard_skills: List[SkillAssessment] = Field(default_factory=list)
    soft_skills: List[SkillAssessment] = Field(default_factory=list)
    technologies: List[SkillAssessment] = Field(default_factory=list)

    questions: List[InterviewQuestion] = Field(default_factory=list)

    risks: List[RiskAssessment] = Field(default_factory=list)

    interviewer_comments: List[str] = Field(default_factory=list)

    recommendation: Recommendation

    adherence_percentage: float = Field(
    default=0.0,
    ge=0.0,
    le=100.0,
    description=(
        "Percentual de aderência documental ponderada "
        "entre currículo e requisitos da vaga"
    ),
)