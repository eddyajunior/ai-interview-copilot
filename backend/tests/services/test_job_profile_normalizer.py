from app.schemas.job_profile import (
    JobProfile,
    JobRequirement,
    RequirementImportance,
    SeniorityLevel,
)
from app.services.job_profile_normalizer import (
    JobProfileNormalizer,
)


def requirement(
    name: str,
    importance: RequirementImportance,
    description: str | None = None,
) -> JobRequirement:
    return JobRequirement(
        name=name,
        importance=importance,
        description=description,
    )


def build_job(
    hard_skills=None,
    technologies=None,
    soft_skills=None,
) -> JobProfile:
    return JobProfile(
        title="Gerente de Engenharia",
        seniority=SeniorityLevel.LEAD,
        summary="Teste",
        hard_skills=hard_skills or [],
        soft_skills=soft_skills or [],
        technologies=technologies or [],
        responsibilities=[],
        differentiators=[],
    )


def test_removes_duplicate_inside_same_group():
    job = build_job(
        technologies=[
            requirement(
                "Cloud",
                RequirementImportance.DESIRED,
            ),
            requirement(
                " cloud ",
                RequirementImportance.REQUIRED,
            ),
        ]
    )

    result = (
        JobProfileNormalizer()
        .normalize(job)
    )

    assert len(result.technologies) == 1
    assert (
        result.technologies[0].importance
        == RequirementImportance.REQUIRED
    )


def test_keeps_most_detailed_description():
    job = build_job(
        hard_skills=[
            requirement(
                "Arquitetura",
                RequirementImportance.REQUIRED,
                "Arquitetura.",
            ),
            requirement(
                "arquitetura",
                RequirementImportance.REQUIRED,
                (
                    "Experiência com arquitetura "
                    "distribuída e escalável."
                ),
            ),
        ]
    )

    result = (
        JobProfileNormalizer()
        .normalize(job)
    )

    assert len(result.hard_skills) == 1
    assert result.hard_skills[
        0
    ].description == (
        "Experiência com arquitetura "
        "distribuída e escalável."
    )


def test_technology_wins_over_hard_skill():
    job = build_job(
        hard_skills=[
            requirement(
                "Cloud",
                RequirementImportance.REQUIRED,
            )
        ],
        technologies=[
            requirement(
                "Cloud",
                RequirementImportance.REQUIRED,
            )
        ],
    )

    result = (
        JobProfileNormalizer()
        .normalize(job)
    )

    assert result.hard_skills == []
    assert len(result.technologies) == 1
    assert (
        result.technologies[0].name
        == "Cloud"
    )


def test_soft_skill_wins_over_hard_skill():
    job = build_job(
        hard_skills=[
            requirement(
                "Comunicação",
                RequirementImportance.REQUIRED,
            )
        ],
        soft_skills=[
            requirement(
                "Comunicação",
                RequirementImportance.REQUIRED,
            )
        ],
    )

    result = (
        JobProfileNormalizer()
        .normalize(job)
    )

    assert result.hard_skills == []
    assert len(result.soft_skills) == 1


def test_does_not_merge_semantically_similar_names():
    job = build_job(
        technologies=[
            requirement(
                "Cloud",
                RequirementImportance.REQUIRED,
            ),
            requirement(
                "Cloud Computing",
                RequirementImportance.REQUIRED,
            ),
        ]
    )

    result = (
        JobProfileNormalizer()
        .normalize(job)
    )

    assert len(result.technologies) == 2