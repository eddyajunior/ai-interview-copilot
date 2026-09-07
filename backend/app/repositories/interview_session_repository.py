import json
from pathlib import Path
from uuid import UUID

from app.schemas.interview_session import InterviewSession


class InterviewSessionRepository:
    def __init__(
        self,
        storage_path: Path | None = None,
    ):
        self.storage_path = storage_path or Path(
            "data/interview_sessions"
        )

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        session: InterviewSession,
    ) -> InterviewSession:
        file_path = self._get_file_path(
            session.session_id
        )

        file_path.write_text(
            session.model_dump_json(
                indent=2,
            ),
            encoding="utf-8",
        )

        return session

    def get(
        self,
        session_id: UUID,
    ) -> InterviewSession | None:
        file_path = self._get_file_path(
            session_id
        )

        if not file_path.exists():
            return None

        data = json.loads(
            file_path.read_text(
                encoding="utf-8",
            )
        )

        return InterviewSession.model_validate(
            data
        )

    def _get_file_path(
        self,
        session_id: UUID,
    ) -> Path:
        return (
            self.storage_path /
            f"{session_id}.json"
        )


    def update(
    self,
    session: InterviewSession,
    ) -> InterviewSession:
        file_path = self._get_file_path(
            session.session_id
        )

        if not file_path.exists():
            raise FileNotFoundError(
                str(session.session_id)
            )

        return self.save(session)