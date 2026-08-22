from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict


class RequirementImportance(str, Enum):
    REQUIRED = "required"
    DESIRED = "desired"
    OPTIONAL = "optional"


class SeniorityLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    SPECIALIST = "specialist"
    LEAD = "lead"


class JobRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    importance: RequirementImportance
    description: str | None


class JobProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    seniority: SeniorityLevel | None
    summary: str

    hard_skills: List[JobRequirement]
    soft_skills: List[JobRequirement]
    technologies: List[JobRequirement]

    responsibilities: List[str]
    differentiators: List[str]