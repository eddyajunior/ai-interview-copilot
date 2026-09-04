from unittest.mock import Mock

from app.services.assessment_orchestrator import (
    AssessmentOrchestrator,
)


def build_orchestrator():
    job_analyzer = Mock()
    resume_analyzer = Mock()
    candidate_scorer = Mock()
    interview_service = Mock()
    risk_service = Mock()
    summary_service = Mock()

    orchestrator = AssessmentOrchestrator(
        job_analyzer=job_analyzer,
        resume_analyzer=resume_analyzer,
        candidate_scorer=candidate_scorer,
        interview_service=interview_service,
        risk_service=risk_service,
        summary_service=summary_service,
    )

    return (
        orchestrator,
        job_analyzer,
        resume_analyzer,
        candidate_scorer,
        interview_service,
        risk_service,
        summary_service,
    )


def test_executes_complete_assessment_flow():
    (
        orchestrator,
        job_analyzer,
        resume_analyzer,
        candidate_scorer,
        interview_service,
        risk_service,
        summary_service,
    ) = build_orchestrator()

    job_document = Mock()
    resume_document = Mock()

    job_profile = Mock()
    resume_profile = Mock()

    scored_assessment = Mock()
    interview_assessment = Mock()
    risk_assessment = Mock()
    final_assessment = Mock()

    job_analyzer.analyze.return_value = (
        job_profile
    )

    resume_analyzer.analyze.return_value = (
        resume_profile
    )

    (
        candidate_scorer
        .build_candidate_assessment
        .return_value
    ) = scored_assessment

    interview_service.enrich.return_value = (
        interview_assessment
    )

    risk_service.enrich.return_value = (
        risk_assessment
    )

    summary_service.enrich.return_value = (
        final_assessment
    )

    result = orchestrator.execute(
        job_document,
        resume_document,
    )

    assert result is final_assessment

    job_analyzer.analyze.assert_called_once_with(
        job_document
    )

    resume_analyzer.analyze.assert_called_once_with(
        resume_document
    )

    (
        candidate_scorer
        .build_candidate_assessment
        .assert_called_once_with(
            job_profile,
            resume_profile,
        )
    )

    interview_service.enrich.assert_called_once_with(
        scored_assessment
    )

    risk_service.enrich.assert_called_once_with(
        interview_assessment
    )

    summary_service.enrich.assert_called_once_with(
        risk_assessment
    )


def test_preserves_pipeline_order():
    (
        orchestrator,
        job_analyzer,
        resume_analyzer,
        candidate_scorer,
        interview_service,
        risk_service,
        summary_service,
    ) = build_orchestrator()

    calls = []

    job_analyzer.analyze.side_effect = (
        lambda document: (
            calls.append("job")
            or "job-profile"
        )
    )

    resume_analyzer.analyze.side_effect = (
        lambda document: (
            calls.append("resume")
            or "resume-profile"
        )
    )

    (
        candidate_scorer
        .build_candidate_assessment
        .side_effect
    ) = lambda job, resume: (
        calls.append("scoring")
        or "scored"
    )

    interview_service.enrich.side_effect = (
        lambda assessment: (
            calls.append("interview")
            or "interviewed"
        )
    )

    risk_service.enrich.side_effect = (
        lambda assessment: (
            calls.append("risk")
            or "risked"
        )
    )

    summary_service.enrich.side_effect = (
        lambda assessment: (
            calls.append("summary")
            or "final"
        )
    )

    orchestrator.execute(
        Mock(),
        Mock(),
    )

    assert calls == [
        "job",
        "resume",
        "scoring",
        "interview",
        "risk",
        "summary",
    ]


def test_returns_summary_enriched_assessment():
    (
        orchestrator,
        job_analyzer,
        resume_analyzer,
        candidate_scorer,
        interview_service,
        risk_service,
        summary_service,
    ) = build_orchestrator()

    job_analyzer.analyze.return_value = "job"
    resume_analyzer.analyze.return_value = "resume"

    (
        candidate_scorer
        .build_candidate_assessment
        .return_value
    ) = "scored"

    interview_service.enrich.return_value = (
        "interviewed"
    )

    risk_service.enrich.return_value = (
        "risked"
    )

    summary_service.enrich.return_value = (
        "final-assessment"
    )

    result = orchestrator.execute(
        Mock(),
        Mock(),
    )

    assert result == "final-assessment"