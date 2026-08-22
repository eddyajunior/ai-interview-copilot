from app.schemas.job_profile import (
    JobProfile,
    JobRequirement,
    RequirementImportance,
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
            )
        ],
        soft_skills=[
            JobRequirement(
                name="Comunicação",
                importance=RequirementImportance.REQUIRED,
            )
        ],
        technologies=[
            JobRequirement(
                name="Java",
                importance=RequirementImportance.REQUIRED,
            ),
            JobRequirement(
                name="Kafka",
                importance=RequirementImportance.DESIRED,
            ),
        ],
        responsibilities=[
            "Desenvolver soluções escaláveis",
            "Participar de decisões arquiteturais",
        ],
    )

    assert job.title == "Senior Software Engineer"
    assert job.technologies[0].name == "Java"
    assert job.technologies[1].importance == RequirementImportance.DESIRED