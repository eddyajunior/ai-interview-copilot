from pathlib import Path

from app.repositories.interview_session_repository import (
    InterviewSessionRepository,
)
from app.schemas.interview_session import (
    InterviewSession,
)


def test_save_and_get_interview_session(
    tmp_path: Path,
):
    repository = InterviewSessionRepository(
        storage_path=tmp_path
    )

    session = InterviewSession(
        candidate_name="Edson Amaral",
        job_title="Engineering Manager",
    )

    repository.save(session)

    recovered = repository.get(
        session.session_id
    )

    assert recovered is not None
    assert (
        recovered.session_id
        == session.session_id
    )
    assert (
        recovered.candidate_name
        == "Edson Amaral"
    )
    assert (
        recovered.job_title
        == "Engineering Manager"
    )


def test_get_returns_none_when_session_does_not_exist(
    tmp_path: Path,
):
    repository = InterviewSessionRepository(
        storage_path=tmp_path
    )

    session = InterviewSession(
        job_title="Engineering Manager",
    )

    result = repository.get(
        session.session_id
    )

    assert result is None

def test_update_existing_interview_session(
    tmp_path: Path,
):
    repository = InterviewSessionRepository(
        storage_path=tmp_path
    )

    session = InterviewSession(
        candidate_name="Edson Amaral",
        job_title="Engineering Manager",
    )

    repository.save(session)

    session.final_notes = (
        "Entrevista concluída com boa avaliação."
    )

    updated = repository.update(session)

    recovered = repository.get(
        session.session_id
    )

    assert updated.final_notes == (
        "Entrevista concluída com boa avaliação."
    )

    assert recovered is not None

    assert recovered.final_notes == (
        "Entrevista concluída com boa avaliação."
    )


def test_update_raises_when_session_does_not_exist(
    tmp_path: Path,
):
    repository = InterviewSessionRepository(
        storage_path=tmp_path
    )

    session = InterviewSession(
        job_title="Engineering Manager",
    )

    try:
        repository.update(session)
    except FileNotFoundError:
        return

    raise AssertionError(
        "Expected FileNotFoundError"
    )