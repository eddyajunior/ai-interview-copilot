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
        professional_summary="Engenheiro de software com experiência em sistemas distribuídos.",
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
            )
        ],
        certifications=[
            ResumeCertification(
                name="AWS Solutions Architect",
                issuer="AWS",
            )
        ],
        hard_skills=[
            ResumeSkillEvidence(
                skill="Arquitetura de Software",
                evidence=[
                    "Participação em decisões arquiteturais",
                ],
            )
        ],
        technologies=[
            ResumeSkillEvidence(
                skill="Kafka",
                evidence=[
                    "Utilização em arquitetura de microsserviços",
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