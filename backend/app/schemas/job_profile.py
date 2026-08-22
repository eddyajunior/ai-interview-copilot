from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class RequirementImportance(str, Enum):
    REQUIRED = "required"
    DESIRED = "desired"
    OPTIONAL = "optional"


class JobRequirement(BaseModel):
    name: str
    importance: RequirementImportance
    description: str | None = None


class JobProfile(BaseModel):
    title: str
    seniority: str | None = None

    summary: str

    hard_skills: List[JobRequirement] = Field(default_factory=list)
    soft_skills: List[JobRequirement] = Field(default_factory=list)
    technologies: List[JobRequirement] = Field(default_factory=list)

    responsibilities: List[str] = Field(default_factory=list)
    differentiators: List[str] = Field(default_factory=list)