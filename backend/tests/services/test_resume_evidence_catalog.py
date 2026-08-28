from app.schemas.evidence import (
    Evidence,
    EvidenceSource,
)
from app.schemas.resume_profile import (
    ResumeEducation,
    ResumeExperience,
    ResumeProfile,
    ResumeSkillEvidence,
)
from app.services.resume_evidence_catalog import (
    ResumeEvidenceCatalog,
)


def build_resume():
    return ResumeProfile(
        candidate_name="Candidate",
        professional_summary=(
            "Líder de Engenharia de Software."
        ),
        experiences=[
            ResumeExperience(
                company="Empresa X",
                role="Engineering Manager",
                start_date=None,
                end_date=None,
                responsibilities=[
                    "Liderança técnica de squads."
                ],
                achievements=[
                    "Redução de custos cloud em 30%."
                ],
                technologies=[
                    "AWS"
                ],
            )
        ],
        education=[
            ResumeEducation(
                institution="Universidade X",
                course=(
                    "Análise e Desenvolvimento "
                    "de Sistemas"
                ),
                level="Graduação",
                completion_date="2012",
            )
        ],
        certifications=[],
        hard_skills=[
            ResumeSkillEvidence(
                skill="FinOps",
                evidence=[
                    Evidence(
                        text=(
                            "Atuação com FinOps."
                        ),
                        source=(
                            EvidenceSource.EXPERIENCE
                        ),
                        source_reference="Empresa X",
                        page=1,
                    )
                ],
            )
        ],
        soft_skill_evidences=[],
        technologies=[],
        leadership_evidences=[],
        measurable_results=[],
    )


def test_builds_evidence_catalog():
    catalog = ResumeEvidenceCatalog().build(
        build_resume()
    )

    texts = {
        evidence.text
        for evidence in catalog.evidences
    }

    assert (
        "Atuação com FinOps."
        in texts
    )

    assert (
        "Líder de Engenharia de Software."
        in texts
    )

    assert (
        "Liderança técnica de squads."
        in texts
    )

    assert (
        "Redução de custos cloud em 30%."
        in texts
    )


def test_adds_education_as_traceable_evidence():
    catalog = ResumeEvidenceCatalog().build(
        build_resume()
    )

    education = next(
        evidence
        for evidence in catalog.evidences
        if evidence.source
        == EvidenceSource.EDUCATION
    )

    assert (
        "Análise e Desenvolvimento de Sistemas"
        in education.text
    )


def test_deduplicates_evidence():
    resume = build_resume()

    resume.hard_skills.append(
        ResumeSkillEvidence(
            skill="Cloud",
            evidence=[
                Evidence(
                    text="Atuação com FinOps.",
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa X",
                    page=1,
                )
            ],
        )
    )

    catalog = ResumeEvidenceCatalog().build(
        resume
    )

    matches = [
        evidence
        for evidence in catalog.evidences
        if evidence.text
        == "Atuação com FinOps."
    ]

    assert len(matches) == 1