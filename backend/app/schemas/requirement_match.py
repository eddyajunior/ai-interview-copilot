from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.schemas.evidence import Evidence


class MatchType(str, Enum):
    EXACT = "exact"
    SEMANTIC = "semantic"
    PARTIAL = "partial"
    NONE = "none"


class RequirementMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_name: str
    matched_skill_names: list[str]
    match_type: MatchType

    evidences: list[Evidence]

    justification: str


class RequirementMatchSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    matches: list[RequirementMatch]