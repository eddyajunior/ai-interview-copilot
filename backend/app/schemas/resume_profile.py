from typing import List

from pydantic import BaseModel, Field

from app.schemas.evidence import Evidence


class ResumeExperience(BaseModel):
    company: str | None = None
    role: str
    start_date: str | None = None
    end_date: str | None = None

    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class ResumeEducation(BaseModel):
    institution: str | None = None
    course: str
    level: str | None = None
    completion_date: str | None = None


class ResumeCertification(BaseModel):
    name: str
    issuer: str | None = None
    date: str | None = None


class ResumeSkillEvidence(BaseModel):
    skill: str
    evidence: List[Evidence] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    candidate_name: str | None = None
    professional_summary: str | None = None

    experiences: List[ResumeExperience] = Field(default_factory=list)
    education: List[ResumeEducation] = Field(default_factory=list)
    certifications: List[ResumeCertification] = Field(default_factory=list)

    hard_skills: List[ResumeSkillEvidence] = Field(default_factory=list)
    soft_skill_evidences: List[ResumeSkillEvidence] = Field(default_factory=list)
    technologies: List[ResumeSkillEvidence] = Field(default_factory=list)

    leadership_evidences: List[str] = Field(default_factory=list)
    measurable_results: List[str] = Field(default_factory=list)