from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.interview_session import (
    InterviewEvidenceStrength,
    InterviewQuestionRecord,
    InterviewQuestionStatus,
    InterviewResponseEvaluation,
    InterviewSession,
)


def test_creates_interview_question_with_defaults():
    question = InterviewQuestionRecord(
        question_index=0,
        competency="Microsserviços",
        question=(
            "Conte sobre uma arquitetura de "
            "microsserviços que você projetou."
        ),
    )

    assert question.question_index == 0
    assert question.status == (
        InterviewQuestionStatus.PENDING
    )

    assert question.evaluation == (
        InterviewResponseEvaluation.NOT_EVALUATED
    )

    assert question.evidence_strength == (
        InterviewEvidenceStrength.NOT_EVALUATED
    )

    assert question.interviewer_notes is None
    assert question.response_summary is None


def test_creates_completed_interview_question():
    question = InterviewQuestionRecord(
        question_index=1,
        competency="Liderança",
        question=(
            "Como você atua em conflitos técnicos?"
        ),
        status=InterviewQuestionStatus.ASKED,
        interviewer_notes=(
            "Trouxe exemplo concreto envolvendo "
            "duas equipes."
        ),
        response_summary=(
            "Mediou a decisão usando dados e "
            "critérios arquiteturais."
        ),
        evaluation=(
            InterviewResponseEvaluation.EXCEEDS
        ),
        evidence_strength=(
            InterviewEvidenceStrength.HIGH
        ),
    )

    assert question.status == (
        InterviewQuestionStatus.ASKED
    )

    assert question.evaluation == (
        InterviewResponseEvaluation.EXCEEDS
    )

    assert question.evidence_strength == (
        InterviewEvidenceStrength.HIGH
    )


def test_rejects_negative_question_index():
    with pytest.raises(ValidationError):
        InterviewQuestionRecord(
            question_index=-1,
            competency="Python",
            question="Qual sua experiência com Python?",
        )


def test_rejects_empty_competency():
    with pytest.raises(ValidationError):
        InterviewQuestionRecord(
            question_index=0,
            competency="",
            question="Pergunta válida",
        )


def test_creates_interview_session():
    started_at = datetime(
        2026,
        9,
        6,
        10,
        0,
    )

    session = InterviewSession(
        candidate_name="Candidato Teste",
        job_title="Engineering Manager",
        started_at=started_at,
        questions=[
            InterviewQuestionRecord(
                question_index=0,
                competency="Liderança",
                question=(
                    "Conte sobre uma decisão "
                    "difícil de liderança."
                ),
            ),
        ],
    )

    assert session.candidate_name == (
        "Candidato Teste"
    )

    assert session.job_title == (
        "Engineering Manager"
    )

    assert session.started_at == started_at
    assert session.completed_at is None
    assert len(session.questions) == 1
    assert session.final_notes is None


def test_session_questions_are_not_shared():
    session_one = InterviewSession(
        job_title="Engineering Manager",
    )

    session_two = InterviewSession(
        job_title="Tech Lead",
    )

    session_one.questions.append(
        InterviewQuestionRecord(
            question_index=0,
            competency="Arquitetura",
            question="Pergunta",
        )
    )

    assert len(session_one.questions) == 1
    assert session_two.questions == []


def test_sessions_receive_unique_ids():
    session_one = InterviewSession(
        job_title="Engineering Manager",
    )

    session_two = InterviewSession(
        job_title="Engineering Manager",
    )

    assert session_one.session_id is not None
    assert session_two.session_id is not None

    assert (
        session_one.session_id
        != session_two.session_id
    )