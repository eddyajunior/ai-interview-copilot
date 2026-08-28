from app.schemas.evidence import Evidence, EvidenceSource

from app.schemas.resume_profile import (
    ResumeCertification,
    ResumeEducation,
    ResumeExperience,
    ResumeProfile,
    ResumeSkillEvidence,
)


def test_resume_profile_valid():
    resume = ResumeProfile(
        candidate_name="João Silva",
        professional_summary=(
            "Engenheiro de software com experiência em sistemas distribuídos."
        ),
        experiences=[
            ResumeExperience(
                company="Empresa X",
                role="Senior Software Engineer",
                start_date="2022",
                end_date="2026",
                responsibilities=[
                    "Desenvolvimento de microsserviços",
                    "Participação em decisões arquiteturais",
                ],
                achievements=[
                    "Redução de 30% no tempo de processamento",
                ],
                technologies=[
                    "Java",
                    "AWS",
                    "Kafka",
                ],
            )
        ],
        education=[
            ResumeEducation(
                institution="Universidade X",
                course="Ciência da Computação",
                level="Bacharelado",
                completion_date=None,
            )
        ],
        certifications=[
            ResumeCertification(
                name="AWS Solutions Architect",
                issuer="AWS",
                date=None,
            )
        ],
        hard_skills=[
            ResumeSkillEvidence(
                skill="Arquitetura de Software",
                evidence=[
                    Evidence(
                        text="Participação em decisões arquiteturais",
                        source=EvidenceSource.EXPERIENCE,
                        source_reference="Senior Software Engineer - Empresa X",
                        page=None,
                    )
                ],
            )
        ],
        soft_skill_evidences=[],
        technologies=[
            ResumeSkillEvidence(
                skill="Kafka",
                evidence=[
                    Evidence(
                        text="Utilização em arquitetura de microsserviços",
                        source=EvidenceSource.EXPERIENCE,
                        source_reference="Senior Software Engineer - Empresa X",
                        page=None,
                    )
                ],
            )
        ],
        leadership_evidences=[
            "Atuação como referência técnica do time",
        ],
        measurable_results=[
            "Redução de 30% no tempo de processamento",
        ],
    )

    assert resume.candidate_name == "João Silva"
    assert resume.experiences[0].role == "Senior Software Engineer"
    assert "Kafka" in resume.experiences[0].technologies
    assert resume.technologies[0].skill == "Kafka"
    assert resume.technologies[0].evidence[0].source == EvidenceSource.EXPERIENCE