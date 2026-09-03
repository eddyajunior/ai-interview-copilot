from pydantic import BaseModel, ConfigDict


class AssessmentRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    short_term: str
    medium_term: str
    long_term: str


class AssessmentSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interviewer_comments: list[str]
    recommendation: AssessmentRecommendation