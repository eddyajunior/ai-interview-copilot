from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.candidate_assessment import (
    CandidateAssessment,
)
from app.schemas.interview_session import (
    InterviewSession,
)
from app.services.interview_session_factory import (
    InterviewSessionFactory,
)
from app.repositories.interview_session_repository import (
    InterviewSessionRepository,
)



router = APIRouter(
    prefix="/api/v1/interview-sessions",
    tags=["interview-sessions"],
)

def get_interview_session_repository():
    return InterviewSessionRepository()

def get_interview_session_factory():
    return InterviewSessionFactory()


@router.post(
    "",
    response_model=InterviewSession,
    status_code=status.HTTP_201_CREATED,
)
def create_interview_session(
    assessment: CandidateAssessment,
    factory: InterviewSessionFactory = Depends(
        get_interview_session_factory
    ),
    repository: InterviewSessionRepository = Depends(
        get_interview_session_repository
    ),
) -> InterviewSession:
    session = factory.create(assessment)

    return repository.save(session)

@router.get(
    "/{session_id}",
    response_model=InterviewSession,
)
def get_interview_session(
    session_id: UUID,
    repository: InterviewSessionRepository = Depends(
        get_interview_session_repository
    ),
) -> InterviewSession:
    session = repository.get(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found.",
        )

    return session

@router.patch(
    "/{session_id}",
    response_model=InterviewSession,
)
def update_interview_session(
    session_id: UUID,
    session: InterviewSession,
    repository: InterviewSessionRepository = Depends(
        get_interview_session_repository
    ),
) -> InterviewSession:
    if session.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Session ID in path does not match "
                "session ID in payload."
            ),
        )

    try:
        return repository.update(session)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found.",
        )