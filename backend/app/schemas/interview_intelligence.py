from enum import Enum

from pydantic import BaseModel, ConfigDict


class InterviewQuestionCategory(str, Enum):
    HARD_SKILL = "hard_skill"
    SOFT_SKILL = "soft_skill"
    TECHNOLOGY = "technology"
    OTHER = "other"


class InterviewQuestionPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InterviewQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: InterviewQuestionCategory
    competency: str
    question: str
    reason: str
    priority: InterviewQuestionPriority
    follow_up: str | None
    what_to_observe: list[str]


class InterviewQuestionSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    questions: list[InterviewQuestion]