from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class InterviewQuestionStatus(str, Enum):
    PENDING = "pending"
    ASKED = "asked"
    SKIPPED = "skipped"


class InterviewResponseEvaluation(str, Enum):
    NOT_EVALUATED = "not_evaluated"
    BELOW_EXPECTATION = "below_expectation"
    PARTIALLY_MEETS = "partially_meets"
    MEETS = "meets"
    EXCEEDS = "exceeds"


class InterviewEvidenceStrength(str, Enum):
    NOT_EVALUATED = "not_evaluated"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InterviewQuestionRecord(BaseModel):
    question_index: int = Field(ge=0)

    competency: str = Field(min_length=1)

    question: str = Field(min_length=1)

    status: InterviewQuestionStatus = (
        InterviewQuestionStatus.PENDING
    )

    interviewer_notes: str | None = None

    response_summary: str | None = None

    evaluation: InterviewResponseEvaluation = (
        InterviewResponseEvaluation.NOT_EVALUATED
    )

    evidence_strength: InterviewEvidenceStrength = (
        InterviewEvidenceStrength.NOT_EVALUATED
    )


class InterviewSession(BaseModel):
    session_id: UUID = Field(
        default_factory=uuid4
    )
    
    candidate_name: str | None = None

    job_title: str = Field(min_length=1)

    started_at: datetime | None = None

    completed_at: datetime | None = None

    questions: list[InterviewQuestionRecord] = (
        Field(default_factory=list)
    )

    final_notes: str | None = None