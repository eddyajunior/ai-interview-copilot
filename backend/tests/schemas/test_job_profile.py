import pytest
from pydantic import ValidationError

from app.schemas.job_profile import (
    JobProfile,
    JobRequirement,
    RequirementImportance,
    SeniorityLevel,
)


def test_job_profile_valid():
    job = JobProfile(
        title="Senior Software Engineer",
        seniority="senior",
        summary="Vaga para desenvolvimento de sistemas distribuídos.",
        hard_skills=[
            JobRequirement(
                name="Arquitetura de Software",
                importance=RequirementImportance.REQUIRED,
                description=None,
            )
        ],
        soft_skills=[
            JobRequirement(
                name="Comunicação",
                importance=RequirementImportance.REQUIRED,
                description=None,
            )
        ],
        technologies=[
            JobRequirement(
                name="Java",
                importance=RequirementImportance.REQUIRED,
                description=None,
            ),
            JobRequirement(
                name="Kafka",
                importance=RequirementImportance.DESIRED,
                description=None,
            ),
        ],
        responsibilities=[
            "Desenvolver soluções escaláveis",
            "Participar de decisões arquiteturais",
        ],
        differentiators=[],
    )

    assert job.title == "Senior Software Engineer"
    assert job.seniority == SeniorityLevel.SENIOR

    assert len(job.hard_skills) == 1
    assert job.hard_skills[0].name == "Arquitetura de Software"

    assert len(job.soft_skills) == 1
    assert job.soft_skills[0].name == "Comunicação"

    assert len(job.technologies) == 2
    assert job.technologies[0].name == "Java"
    assert job.technologies[1].name == "Kafka"

    assert len(job.responsibilities) == 2
    assert job.differentiators == []


def test_job_requirement_requires_description():
    with pytest.raises(ValidationError):
        JobRequirement(
            name="Java",
            importance=RequirementImportance.REQUIRED,
        )

def test_job_profile_rejects_invalid_seniority():
    with pytest.raises(ValidationError):
        JobProfile(
            title="Software Engineer",
            seniority="principal",
            summary="Vaga de engenharia.",
            hard_skills=[],
            soft_skills=[],
            technologies=[],
            responsibilities=[],
            differentiators=[],
        )