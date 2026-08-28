from app.schemas.evidence import (
    Evidence,
    EvidenceSource,
)
from app.schemas.job_profile import (
    JobProfile,
    JobRequirement,
    RequirementImportance,
    SeniorityLevel,
)
from app.schemas.resume_profile import (
    ResumeProfile,
    ResumeSkillEvidence,
)
from app.schemas.scoring import (
    AssessmentStatus,
    EvidenceStrength,
    SkillScore,
)
from app.services.candidate_scorer import (
    CandidateScorer,
    SkillScoreResult,
)
from app.schemas.candidate_assessment import (
    ConfidenceLevel,
    SkillType,
)
from app.schemas.requirement_match import (
    MatchType,
    RequirementMatch,
    RequirementMatchSet,
)


def build_job() -> JobProfile:
    return JobProfile(
        title="Senior Software Engineer",
        seniority=SeniorityLevel.SENIOR,
        summary="Desenvolvimento de sistemas distribuídos.",
        hard_skills=[],
        soft_skills=[],
        technologies=[
            JobRequirement(
                name="Java",
                importance=RequirementImportance.REQUIRED,
                description=None,
            ),
            JobRequirement(
                name="Kafka",
                importance=RequirementImportance.REQUIRED,
                description=None,
            ),
        ],
        responsibilities=[],
        differentiators=[],
    )


def build_resume() -> ResumeProfile:
    return ResumeProfile(
        candidate_name="João Silva",
        professional_summary=None,
        experiences=[],
        education=[],
        certifications=[],
        hard_skills=[],
        soft_skill_evidences=[],
        technologies=[
            ResumeSkillEvidence(
                skill="Java",
                evidence=[
                    Evidence(
                        text="Experiência com Java.",
                        source=EvidenceSource.EXPERIENCE,
                        source_reference="Empresa X",
                        page=1,
                    )
                ],
            )
        ],
        leadership_evidences=[],
        measurable_results=[],
    )


def test_scores_evidenced_technology_as_compatible():
    scorer = CandidateScorer()

    results = scorer.score_technologies(
        build_job(),
        build_resume(),
    )

    java = next(
        item
        for item in results
        if item.name == "Java"
    )

    assert java.score == SkillScore.COMPATIBLE
    assert java.evidence_strength == EvidenceStrength.MEDIUM
    assert java.status == AssessmentStatus.COMPATIBLE
    assert len(java.evidences) == 1


def test_scores_missing_technology_as_not_evidenced():
    scorer = CandidateScorer()

    results = scorer.score_technologies(
        build_job(),
        build_resume(),
    )

    kafka = next(
        item
        for item in results
        if item.name == "Kafka"
    )

    assert kafka.score == SkillScore.NOT_EVIDENCED
    assert kafka.evidence_strength == EvidenceStrength.NONE
    assert kafka.status == AssessmentStatus.NOT_EVIDENCED
    assert kafka.evidences == []


def test_technology_matching_is_case_insensitive():
    job = build_job()
    job.technologies[0].name = "JAVA"

    resume = build_resume()
    resume.technologies[0].skill = "java"

    scorer = CandidateScorer()

    results = scorer.score_technologies(
        job,
        resume,
    )

    java = results[0]

    assert java.score == SkillScore.COMPATIBLE

def test_matches_technology_using_safe_alias():
    job = build_job()
    job.technologies[0].name = "Amazon AWS"

    resume = build_resume()
    resume.technologies[0].skill = "AWS"

    scorer = CandidateScorer()

    results = scorer.score_technologies(
        job,
        resume,
    )

    technology = results[0]

    assert technology.score == SkillScore.COMPATIBLE


def test_matches_dotnet_core_with_dotnet():
    job = build_job()
    job.technologies[0].name = ".NET"

    resume = build_resume()
    resume.technologies[0].skill = ".NET Core"

    scorer = CandidateScorer()

    results = scorer.score_technologies(
        job,
        resume,
    )

    technology = results[0]

    assert technology.score == SkillScore.COMPATIBLE


def test_matches_postgres_with_postgresql():
    job = build_job()
    job.technologies[0].name = "PostgreSQL"

    resume = build_resume()
    resume.technologies[0].skill = "Postgres"

    scorer = CandidateScorer()

    results = scorer.score_technologies(
        job,
        resume,
    )

    technology = results[0]

    assert technology.score == SkillScore.COMPATIBLE


def test_does_not_match_java_with_javascript():
    job = build_job()
    job.technologies[0].name = "Java"

    resume = build_resume()
    resume.technologies[0].skill = "JavaScript"

    scorer = CandidateScorer()

    results = scorer.score_technologies(
        job,
        resume,
    )

    technology = results[0]

    assert technology.score == SkillScore.NOT_EVIDENCED


def test_scores_skill_section_only_as_limited():
    resume = build_resume()

    resume.technologies[0].evidence = [
        Evidence(
            text="Competências: Java.",
            source=EvidenceSource.SKILL_SECTION,
            source_reference="Competências",
            page=1,
        )
    ]

    scorer = CandidateScorer()

    results = scorer.score_technologies(
        build_job(),
        resume,
    )

    java = results[0]

    assert java.score == SkillScore.LIMITED
    assert java.evidence_strength == EvidenceStrength.LOW
    assert java.status == AssessmentStatus.NEEDS_VALIDATION


def test_scores_single_experience_evidence_as_compatible():
    scorer = CandidateScorer()

    results = scorer.score_technologies(
        build_job(),
        build_resume(),
    )

    java = results[0]

    assert java.score == SkillScore.COMPATIBLE
    assert java.evidence_strength == EvidenceStrength.MEDIUM
    assert java.status == AssessmentStatus.COMPATIBLE


def test_scores_multiple_relevant_evidences_as_strong():
    resume = build_resume()

    resume.technologies[0].evidence.append(
        Evidence(
            text="Desenvolvimento de APIs Java.",
            source=EvidenceSource.EXPERIENCE,
            source_reference="Empresa Y",
            page=2,
        )
    )

    scorer = CandidateScorer()

    results = scorer.score_technologies(
        build_job(),
        resume,
    )

    java = results[0]

    assert java.score == SkillScore.STRONG
    assert java.evidence_strength == EvidenceStrength.HIGH
    assert java.status == AssessmentStatus.STRONG


def test_does_not_inflate_score_with_duplicate_evidence():
    resume = build_resume()

    resume.technologies[0].evidence.append(
        Evidence(
            text="Experiência com Java.",
            source=EvidenceSource.EXPERIENCE,
            source_reference="Empresa X",
            page=1,
        )
    )

    scorer = CandidateScorer()

    results = scorer.score_technologies(
        build_job(),
        resume,
    )

    java = results[0]

    assert java.score == SkillScore.COMPATIBLE
    assert len(java.evidences) == 1


def test_scores_multiple_sources_and_measurable_result_as_very_strong():
    resume = build_resume()

    resume.technologies[0].evidence.append(
        Evidence(
            text="Java listado entre as competências técnicas.",
            source=EvidenceSource.SKILL_SECTION,
            source_reference="Competências",
            page=2,
        )
    )

    resume.measurable_results = [
        "Java: redução de 40% no tempo de processamento."
    ]

    scorer = CandidateScorer()

    results = scorer.score_technologies(
        build_job(),
        resume,
    )

    java = results[0]

    assert java.score == SkillScore.VERY_STRONG
    assert java.evidence_strength == EvidenceStrength.HIGH
    assert java.status == AssessmentStatus.STRONG


def test_scores_evidenced_hard_skill():
    job = build_job()

    job.hard_skills = [
        JobRequirement(
            name="Arquitetura distribuída",
            importance=RequirementImportance.REQUIRED,
            description=None,
        )
    ]

    resume = build_resume()

    resume.hard_skills = [
        ResumeSkillEvidence(
            skill="Arquitetura distribuída",
            evidence=[
                Evidence(
                    text=(
                        "Experiência com arquitetura "
                        "distribuída."
                    ),
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa X",
                    page=1,
                )
            ],
        )
    ]

    scorer = CandidateScorer()

    results = scorer.score_hard_skills(
        job,
        resume,
    )

    skill = results[0]

    assert skill.name == "Arquitetura distribuída"
    assert skill.score == SkillScore.COMPATIBLE
    assert skill.evidence_strength == EvidenceStrength.MEDIUM


def test_scores_missing_hard_skill_as_not_evidenced():
    job = build_job()

    job.hard_skills = [
        JobRequirement(
            name="Microsserviços",
            importance=RequirementImportance.REQUIRED,
            description=None,
        )
    ]

    resume = build_resume()

    scorer = CandidateScorer()

    results = scorer.score_hard_skills(
        job,
        resume,
    )

    skill = results[0]

    assert skill.score == SkillScore.NOT_EVIDENCED
    assert skill.status == AssessmentStatus.NOT_EVIDENCED


def test_hard_skill_matching_is_case_insensitive():
    job = build_job()

    job.hard_skills = [
        JobRequirement(
            name="ARQUITETURA DISTRIBUÍDA",
            importance=RequirementImportance.REQUIRED,
            description=None,
        )
    ]

    resume = build_resume()

    resume.hard_skills = [
        ResumeSkillEvidence(
            skill="arquitetura distribuída",
            evidence=[
                Evidence(
                    text="Arquitetura distribuída.",
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa X",
                    page=1,
                )
            ],
        )
    ]

    scorer = CandidateScorer()

    results = scorer.score_hard_skills(
        job,
        resume,
    )

    assert results[0].score == SkillScore.COMPATIBLE


def test_hard_skill_uses_same_evidence_strength_rules():
    job = build_job()

    job.hard_skills = [
        JobRequirement(
            name="FinOps",
            importance=RequirementImportance.REQUIRED,
            description=None,
        )
    ]

    resume = build_resume()

    resume.hard_skills = [
        ResumeSkillEvidence(
            skill="FinOps",
            evidence=[
                Evidence(
                    text="Responsável por iniciativas de FinOps.",
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa X",
                    page=1,
                ),
                Evidence(
                    text="FinOps listado como competência.",
                    source=EvidenceSource.SKILL_SECTION,
                    source_reference="Competências",
                    page=2,
                ),
            ],
        )
    ]

    resume.measurable_results = [
        "FinOps: redução de 30% nos custos de cloud."
    ]

    scorer = CandidateScorer()

    results = scorer.score_hard_skills(
        job,
        resume,
    )

    finops = results[0]

    assert finops.score == SkillScore.VERY_STRONG
    assert finops.evidence_strength == EvidenceStrength.HIGH
    assert finops.status == AssessmentStatus.STRONG

def test_scores_missing_soft_skill_as_not_evidenced():
    job = build_job()

    job.soft_skills = [
        JobRequirement(
            name="Comunicação",
            importance=RequirementImportance.REQUIRED,
            description=None,
        )
    ]

    resume = build_resume()

    scorer = CandidateScorer()

    results = scorer.score_soft_skills(
        job,
        resume,
    )

    communication = results[0]

    assert communication.score == SkillScore.NOT_EVIDENCED
    assert communication.evidence_strength == EvidenceStrength.NONE
    assert communication.status == AssessmentStatus.NOT_EVIDENCED


def test_scores_declared_soft_skill_as_limited():
    job = build_job()

    job.soft_skills = [
        JobRequirement(
            name="Comunicação",
            importance=RequirementImportance.REQUIRED,
            description=None,
        )
    ]

    resume = build_resume()

    resume.soft_skill_evidences = [
        ResumeSkillEvidence(
            skill="Comunicação",
            evidence=[
                Evidence(
                    text="Comunicação entre as competências.",
                    source=EvidenceSource.SKILL_SECTION,
                    source_reference="Competências",
                    page=2,
                )
            ],
        )
    ]

    scorer = CandidateScorer()

    results = scorer.score_soft_skills(
        job,
        resume,
    )

    communication = results[0]

    assert communication.score == SkillScore.LIMITED
    assert communication.evidence_strength == EvidenceStrength.LOW
    assert communication.status == AssessmentStatus.NEEDS_VALIDATION


def test_scores_experience_soft_skill_as_compatible():
    job = build_job()

    job.soft_skills = [
        JobRequirement(
            name="Comunicação",
            importance=RequirementImportance.REQUIRED,
            description=None,
        )
    ]

    resume = build_resume()

    resume.soft_skill_evidences = [
        ResumeSkillEvidence(
            skill="Comunicação",
            evidence=[
                Evidence(
                    text=(
                        "Responsável pela comunicação técnica "
                        "com stakeholders."
                    ),
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa X",
                    page=1,
                )
            ],
        )
    ]

    scorer = CandidateScorer()

    results = scorer.score_soft_skills(
        job,
        resume,
    )

    communication = results[0]

    assert communication.score == SkillScore.COMPATIBLE
    assert communication.evidence_strength == EvidenceStrength.MEDIUM
    assert communication.status == AssessmentStatus.COMPATIBLE


def test_scores_soft_skill_with_multiple_contexts_as_strong():
    job = build_job()

    job.soft_skills = [
        JobRequirement(
            name="Comunicação",
            importance=RequirementImportance.REQUIRED,
            description=None,
        )
    ]

    resume = build_resume()

    resume.soft_skill_evidences = [
        ResumeSkillEvidence(
            skill="Comunicação",
            evidence=[
                Evidence(
                    text=(
                        "Responsável pela comunicação técnica "
                        "com stakeholders."
                    ),
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa X",
                    page=1,
                ),
                Evidence(
                    text=(
                        "Condução de apresentações executivas "
                        "para diferentes áreas."
                    ),
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa Y",
                    page=2,
                ),
            ],
        )
    ]

    scorer = CandidateScorer()

    results = scorer.score_soft_skills(
        job,
        resume,
    )

    communication = results[0]

    assert communication.score == SkillScore.STRONG
    assert communication.evidence_strength == EvidenceStrength.HIGH
    assert communication.status == AssessmentStatus.STRONG


def test_soft_skill_does_not_reach_score_five_from_resume_only():
    job = build_job()

    job.soft_skills = [
        JobRequirement(
            name="Liderança",
            importance=RequirementImportance.REQUIRED,
            description=None,
        )
    ]

    resume = build_resume()

    resume.soft_skill_evidences = [
        ResumeSkillEvidence(
            skill="Liderança",
            evidence=[
                Evidence(
                    text="Liderança de equipe de engenharia.",
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa X",
                    page=1,
                ),
                Evidence(
                    text="Gestão de desenvolvedores.",
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa Y",
                    page=2,
                ),
                Evidence(
                    text="Mentoria e desenvolvimento de pessoas.",
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa Z",
                    page=3,
                ),
            ],
        )
    ]

    scorer = CandidateScorer()

    results = scorer.score_soft_skills(
        job,
        resume,
    )

    leadership = results[0]

    assert leadership.score == SkillScore.STRONG
    assert leadership.score != SkillScore.VERY_STRONG

def test_calculates_full_adherence():
    job = JobProfile(
        title="Software Engineer",
        seniority=SeniorityLevel.SENIOR,
        summary="Test job",
        hard_skills=[],
        soft_skills=[],
        technologies=[
            JobRequirement(
                name="Java",
                importance=RequirementImportance.REQUIRED,
                description=None,
            )
        ],
        responsibilities=[],
        differentiators=[],
    )

    resume = build_resume()

    resume.technologies[0].evidence = [
        Evidence(
            text="Java em experiência profissional.",
            source=EvidenceSource.EXPERIENCE,
            source_reference="Empresa X",
            page=1,
        ),
        Evidence(
            text="Java em competências técnicas.",
            source=EvidenceSource.SKILL_SECTION,
            source_reference="Competências",
            page=2,
        ),
    ]

    resume.measurable_results = [
        "Java: redução de 40% no tempo de processamento."
    ]

    scorer = CandidateScorer()

    result = scorer.calculate_adherence(
        job,
        resume,
    )

    assert result.percentage == 100.0
    assert result.evaluated_requirements == 1


def test_not_evidenced_requirement_contributes_zero():
    job = JobProfile(
        title="Software Engineer",
        seniority=SeniorityLevel.SENIOR,
        summary="Test job",
        hard_skills=[],
        soft_skills=[],
        technologies=[
            JobRequirement(
                name="Kafka",
                importance=RequirementImportance.REQUIRED,
                description=None,
            )
        ],
        responsibilities=[],
        differentiators=[],
    )

    resume = build_resume()

    scorer = CandidateScorer()

    result = scorer.calculate_adherence(
        job,
        resume,
    )

    assert result.percentage == 0.0


def test_compatible_requirement_contributes_fifty_percent():
    job = JobProfile(
        title="Software Engineer",
        seniority=SeniorityLevel.SENIOR,
        summary="Test job",
        hard_skills=[],
        soft_skills=[],
        technologies=[
            JobRequirement(
                name="Java",
                importance=RequirementImportance.REQUIRED,
                description=None,
            )
        ],
        responsibilities=[],
        differentiators=[],
    )

    resume = build_resume()

    scorer = CandidateScorer()

    result = scorer.calculate_adherence(
        job,
        resume,
    )

    assert result.percentage == 50.0


def test_required_requirement_has_more_weight_than_optional():
    job = JobProfile(
        title="Software Engineer",
        seniority=SeniorityLevel.SENIOR,
        summary="Test job",
        hard_skills=[],
        soft_skills=[],
        technologies=[
            JobRequirement(
                name="Kafka",
                importance=RequirementImportance.REQUIRED,
                description=None,
            ),
            JobRequirement(
                name="Java",
                importance=RequirementImportance.OPTIONAL,
                description=None,
            ),
        ],
        responsibilities=[],
        differentiators=[],
    )

    resume = build_resume()

    resume.technologies[0].evidence = [
        Evidence(
            text="Java em experiência profissional.",
            source=EvidenceSource.EXPERIENCE,
            source_reference="Empresa X",
            page=1,
        ),
        Evidence(
            text="Java em outra experiência.",
            source=EvidenceSource.EXPERIENCE,
            source_reference="Empresa Y",
            page=2,
        ),
    ]

    scorer = CandidateScorer()

    result = scorer.calculate_adherence(
        job,
        resume,
    )

    assert result.percentage == 18.75


def test_returns_zero_when_job_has_no_evaluated_requirements():
    job = JobProfile(
        title="Software Engineer",
        seniority=None,
        summary="Test job",
        hard_skills=[],
        soft_skills=[],
        technologies=[],
        responsibilities=[],
        differentiators=[],
    )

    resume = build_resume()

    scorer = CandidateScorer()

    result = scorer.calculate_adherence(
        job,
        resume,
    )

    assert result.percentage == 0.0
    assert result.weighted_score == 0.0
    assert result.maximum_weighted_score == 0.0
    assert result.evaluated_requirements == 0

def test_builds_candidate_assessment():
    scorer = CandidateScorer()

    assessment = scorer.build_candidate_assessment(
        build_job(),
        build_resume(),
    )

    assert assessment.job_title == "Senior Software Engineer"
    assert assessment.adherence_percentage == 25.0

    assert len(assessment.technologies) == 2
    assert len(assessment.hard_skills) == 0
    assert len(assessment.soft_skills) == 0

    assert assessment.questions == []
    assert assessment.risks == []


def test_candidate_assessment_preserves_skill_types():
    scorer = CandidateScorer()

    assessment = scorer.build_candidate_assessment(
        build_job(),
        build_resume(),
    )

    java = next(
        item
        for item in assessment.technologies
        if item.name == "Java"
    )

    assert java.type == SkillType.TECHNOLOGY
    assert java.score == 3
    assert java.confidence == ConfidenceLevel.MEDIUM


def test_candidate_assessment_does_not_call_missing_skill_a_competence_failure():
    scorer = CandidateScorer()

    assessment = scorer.build_candidate_assessment(
        build_job(),
        build_resume(),
    )

    kafka_gap = next(
        item
        for item in assessment.weaknesses
        if "Kafka" in item
    )

    assert "evidência insuficiente" in kafka_gap
    assert "validar" in kafka_gap


def test_soft_skill_confidence_is_capped_at_medium_from_resume():
    job = build_job()

    job.soft_skills = [
        JobRequirement(
            name="Comunicação",
            importance=RequirementImportance.REQUIRED,
            description=None,
        )
    ]

    resume = build_resume()

    resume.soft_skill_evidences = [
        ResumeSkillEvidence(
            skill="Comunicação",
            evidence=[
                Evidence(
                    text="Comunicação com stakeholders.",
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa X",
                    page=1,
                ),
                Evidence(
                    text="Apresentações executivas.",
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa Y",
                    page=2,
                ),
            ],
        )
    ]

    scorer = CandidateScorer()

    assessment = scorer.build_candidate_assessment(
        job,
        resume,
    )

    communication = assessment.soft_skills[0]

    assert communication.score == 4
    assert communication.confidence == ConfidenceLevel.MEDIUM

def test_scores_none_requirement_match_as_not_evidenced():
    scorer = CandidateScorer()

    result = scorer.score_requirement_match(
        RequirementMatch(
            requirement_name="DevOps",
            matched_skill_names=[],
            match_type=MatchType.NONE,
            evidences=[],
            justification=(
                "Nenhuma evidência encontrada."
            ),
        )
    )

    assert result.score == SkillScore.NOT_EVIDENCED
    assert (
        result.status
        == AssessmentStatus.NOT_EVIDENCED
    )


def test_scores_partial_match_with_experience_as_compatible():
    scorer = CandidateScorer()

    result = scorer.score_requirement_match(
        RequirementMatch(
            requirement_name="Cloud e FinOps",
            matched_skill_names=[
                "FinOps",
            ],
            match_type=MatchType.PARTIAL,
            evidences=[
                Evidence(
                    text=(
                        "Reduziu custos cloud "
                        "com práticas de FinOps."
                    ),
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa X",
                    page=1,
                )
            ],
            justification=(
                "FinOps sustenta parcialmente "
                "o requisito."
            ),
        )
    )

    assert result.score == SkillScore.COMPATIBLE


def test_scores_semantic_match_with_multiple_sources_as_strong():
    scorer = CandidateScorer()

    result = scorer.score_requirement_match(
        RequirementMatch(
            requirement_name="Arquitetura de software",
            matched_skill_names=[
                "Arquitetura distribuída",
            ],
            match_type=MatchType.SEMANTIC,
            evidences=[
                Evidence(
                    text=(
                        "Experiência com "
                        "arquitetura distribuída."
                    ),
                    source=(
                        EvidenceSource.PROFESSIONAL_SUMMARY
                    ),
                    source_reference=(
                        "Resumo profissional"
                    ),
                    page=1,
                ),
                Evidence(
                    text=(
                        "Definiu padrões de APIs."
                    ),
                    source=EvidenceSource.EXPERIENCE,
                    source_reference="Empresa X",
                    page=2,
                ),
            ],
            justification=(
                "As evidências sustentam "
                "arquitetura de software."
            ),
        )
    )

    assert result.score == SkillScore.STRONG


def test_scores_requirement_match_set():
    scorer = CandidateScorer()

    results = scorer.score_requirement_matches(
        RequirementMatchSet(
            matches=[
                RequirementMatch(
                    requirement_name="DevOps",
                    matched_skill_names=[],
                    match_type=MatchType.NONE,
                    evidences=[],
                    justification=(
                        "Nenhuma evidência."
                    ),
                ),
                RequirementMatch(
                    requirement_name="FinOps",
                    matched_skill_names=[
                        "FinOps",
                    ],
                    match_type=MatchType.EXACT,
                    evidences=[
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
                    justification=(
                        "Correspondência direta."
                    ),
                ),
            ]
        )
    )

    assert len(results) == 2
    assert (
        results[0].score
        == SkillScore.NOT_EVIDENCED
    )
    assert (
        results[1].score
        == SkillScore.COMPATIBLE
    )


def test_calculates_adherence_from_requirement_scores():
    scorer = CandidateScorer()

    job = JobProfile(
        title="Engineering Manager",
        seniority=None,
        summary="",
        hard_skills=[
            JobRequirement(
                name="Arquitetura",
                importance=(
                    RequirementImportance.REQUIRED
                ),
                description=None,
            )
        ],
        soft_skills=[
            JobRequirement(
                name="Comunicação",
                importance=(
                    RequirementImportance.DESIRED
                ),
                description=None,
            )
        ],
        technologies=[
            JobRequirement(
                name="AWS",
                importance=(
                    RequirementImportance.REQUIRED
                ),
                description=None,
            )
        ],
        responsibilities=[],
        differentiators=[],
    )

    technology_scores = [
        SkillScoreResult(
            name="AWS",
            score=SkillScore.STRONG,
            evidence_strength=(
                EvidenceStrength.HIGH
            ),
            status=AssessmentStatus.STRONG,
            evidences=[],
            justification="",
        )
    ]

    hard_skill_scores = [
        SkillScoreResult(
            name="Arquitetura",
            score=SkillScore.COMPATIBLE,
            evidence_strength=(
                EvidenceStrength.MEDIUM
            ),
            status=AssessmentStatus.COMPATIBLE,
            evidences=[],
            justification="",
        )
    ]

    soft_skill_scores = [
        SkillScoreResult(
            name="Comunicação",
            score=SkillScore.NOT_EVIDENCED,
            evidence_strength=(
                EvidenceStrength.NONE
            ),
            status=(
                AssessmentStatus.NOT_EVIDENCED
            ),
            evidences=[],
            justification="",
        )
    ]

    result = (
        scorer.calculate_adherence_from_scores(
            job=job,
            technology_scores=technology_scores,
            hard_skill_scores=hard_skill_scores,
            soft_skill_scores=soft_skill_scores,
        )
    )

    assert result.evaluated_requirements == 3

    assert result.maximum_weighted_score == 8

    assert result.weighted_score == 3.75

    assert result.percentage == 46.88


def test_education_evidence_can_be_compatible():
    scorer = CandidateScorer()

    match = RequirementMatch(
        requirement_name=(
            "Formação superior em área correlata"
        ),
        matched_skill_names=[],
        match_type=MatchType.SEMANTIC,
        evidences=[
            Evidence(
                text=(
                    "Engenharia de Software — "
                    "Bacharelado"
                ),
                source=EvidenceSource.EDUCATION,
                source_reference=(
                    "Universidade X"
                ),
                page=None,
            )
        ],
        justification=(
            "A formação apresentada é "
            "diretamente relacionada ao requisito."
        ),
    )

    result = scorer.score_requirement_match(
        match
    )

    assert (
        result.score
        == SkillScore.COMPATIBLE
    )
    assert (
        result.evidence_strength
        == EvidenceStrength.MEDIUM
    )
    assert (
        result.status
        == AssessmentStatus.COMPATIBLE
    )

def test_certification_evidence_can_be_compatible():
    scorer = CandidateScorer()

    match = RequirementMatch(
        requirement_name="Certificação AWS",
        matched_skill_names=[],
        match_type=MatchType.EXACT,
        evidences=[
            Evidence(
                text=(
                    "AWS Certified Solutions "
                    "Architect"
                ),
                source=EvidenceSource.CERTIFICATION,
                source_reference="AWS",
                page=None,
            )
        ],
        justification=(
            "A certificação exigida está "
            "explicitamente registrada."
        ),
    )

    result = scorer.score_requirement_match(
        match
    )

    assert (
        result.score
        == SkillScore.COMPATIBLE
    )