from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.evidence import Evidence


class ResumeExperience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: str | None
    role: str

    start_date: str | None
    end_date: str | None

    responsibilities: List[str]
    achievements: List[str]
    technologies: List[str]


class ResumeEducation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: str | None
    course: str

    level: str | None
    completion_date: str | None


class ResumeCertification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    issuer: str | None
    date: str | None


class ResumeSkillEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill: str
    evidence: List[Evidence]


class ResumeProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_name: str | None
    professional_summary: str | None

    experiences: List[ResumeExperience]
    education: List[ResumeEducation]
    certifications: List[ResumeCertification]

    hard_skills: List[ResumeSkillEvidence]
    soft_skill_evidences: List[ResumeSkillEvidence]
    technologies: List[ResumeSkillEvidence]

    leadership_evidences: List[str]
    measurable_results: List[str]