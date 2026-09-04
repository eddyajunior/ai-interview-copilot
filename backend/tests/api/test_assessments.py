from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.assessments import (
    get_assessment_orchestrator,
    get_document_parser,
    router,
)
from app.schemas.document import (
    DocumentPage,
    DocumentType,
    ParsedDocument,
)
from pathlib import Path

def build_parsed_document(
    filename: str,
    document_type: DocumentType,
) -> ParsedDocument:
    content = "conteúdo de teste"

    return ParsedDocument(
        filename=filename,
        document_type=document_type,
        content=content,
        character_count=len(content),
        page_count=1,
        pages=[
            DocumentPage(
                number=1,
                content=content,
            )
        ],
    )


def create_test_client(
    document_parser: Mock,
    orchestrator: Mock,
) -> TestClient:
    app = FastAPI()

    app.include_router(router)

    app.dependency_overrides[
        get_document_parser
    ] = lambda: document_parser

    app.dependency_overrides[
        get_assessment_orchestrator
    ] = lambda: orchestrator

    return TestClient(app)


def test_creates_assessment_successfully():
    document_parser = Mock()
    orchestrator = Mock()

    job_document = build_parsed_document(
        filename="job_description",
        document_type=DocumentType.RAW_TEXT,
    )

    resume_document = build_parsed_document(
        filename="resume.pdf",
        document_type=DocumentType.PDF,
    )

    expected_assessment = {
        "candidate_name": None,
        "job_title": "Software Engineer",
        "summary": "Resumo",
        "adherence_percentage": 50.0,
        "strengths": [],
        "weaknesses": [],
        "hard_skills": [],
        "soft_skills": [],
        "technologies": [],
        "questions": [],
        "risks": [],
        "interviewer_comments": [],
        "recommendation": {
            "short_term": "Curto prazo",
            "medium_term": "Médio prazo",
            "long_term": "Longo prazo",
        },
    }

    document_parser.parse_text.return_value = (
        job_document
    )

    document_parser.parse.return_value = (
        resume_document
    )

    orchestrator.execute.return_value = (
        expected_assessment
    )

    client = create_test_client(
        document_parser,
        orchestrator,
    )

    response = client.post(
        "/api/v1/assessments",
        data={
            "job_description": (
                "Descrição da vaga"
            ),
        },
        files={
            "resume": (
                "resume.pdf",
                b"conteudo-do-pdf",
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["job_title"] == (
        "Software Engineer"
    )

    assert body["adherence_percentage"] == 50.0

    document_parser.parse_text.assert_called_once_with(
        "Descrição da vaga",
        source_name="job_description",
    )

    document_parser.parse.assert_called_once()

    orchestrator.execute.assert_called_once_with(
        job_document,
        resume_document,
    )


def test_rejects_empty_job_description():
    document_parser = Mock()
    orchestrator = Mock()

    client = create_test_client(
        document_parser,
        orchestrator,
    )

    response = client.post(
        "/api/v1/assessments",
        data={
            "job_description": "   ",
        },
        files={
            "resume": (
                "resume.pdf",
                b"conteudo-do-pdf",
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": (
            "A descrição da vaga não pode estar vazia."
        )
    }

    document_parser.parse_text.assert_not_called()
    orchestrator.execute.assert_not_called()


def test_rejects_unsupported_resume_format():
    document_parser = Mock()
    orchestrator = Mock()

    client = create_test_client(
        document_parser,
        orchestrator,
    )

    response = client.post(
        "/api/v1/assessments",
        data={
            "job_description": (
                "Descrição válida da vaga"
            ),
        },
        files={
            "resume": (
                "resume.exe",
                b"arquivo-invalido",
                "application/octet-stream",
            ),
        },
    )

    assert response.status_code == 415

    assert response.json() == {
        "detail": (
            "Formato de currículo não suportado. "
            "Utilize TXT, PDF ou DOCX."
        )
    }

    document_parser.parse_text.assert_not_called()
    orchestrator.execute.assert_not_called()


def test_rejects_empty_resume():
    document_parser = Mock()
    orchestrator = Mock()

    client = create_test_client(
        document_parser,
        orchestrator,
    )

    response = client.post(
        "/api/v1/assessments",
        data={
            "job_description": (
                "Descrição válida da vaga"
            ),
        },
        files={
            "resume": (
                "resume.pdf",
                b"",
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": (
            "O arquivo do currículo não pode estar vazio."
        )
    }

    document_parser.parse_text.assert_not_called()
    orchestrator.execute.assert_not_called()


def test_removes_temporary_file_when_orchestrator_fails(
    monkeypatch,
):
    document_parser = Mock()
    orchestrator = Mock()

    job_document = build_parsed_document(
        filename="job_description",
        document_type=DocumentType.RAW_TEXT,
    )

    resume_document = build_parsed_document(
        filename="resume.pdf",
        document_type=DocumentType.PDF,
    )

    document_parser.parse_text.return_value = (
        job_document
    )

    document_parser.parse.return_value = (
        resume_document
    )

    orchestrator.execute.side_effect = RuntimeError(
        "erro interno"
    )

    temporary_files = []

    from app.api import assessments

    original_named_temporary_file = (
        assessments.NamedTemporaryFile
    )

    def tracked_named_temporary_file(*args, **kwargs):
        temporary_file = original_named_temporary_file(
            *args,
            **kwargs,
        )

        temporary_files.append(
            Path(temporary_file.name)
        )

        return temporary_file

    monkeypatch.setattr(
        assessments,
        "NamedTemporaryFile",
        tracked_named_temporary_file,
    )

    client = create_test_client(
        document_parser,
        orchestrator,
    )

    response = client.post(
        "/api/v1/assessments",
        data={
            "job_description": (
                "Descrição válida da vaga"
            ),
        },
        files={
            "resume": (
                "resume.pdf",
                b"conteudo-do-pdf",
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 500

    assert len(temporary_files) == 1

    assert not temporary_files[0].exists()


def test_returns_controlled_internal_server_error():
    document_parser = Mock()
    orchestrator = Mock()

    job_document = build_parsed_document(
        filename="job_description",
        document_type=DocumentType.RAW_TEXT,
    )

    resume_document = build_parsed_document(
        filename="resume.pdf",
        document_type=DocumentType.PDF,
    )

    document_parser.parse_text.return_value = (
        job_document
    )

    document_parser.parse.return_value = (
        resume_document
    )

    orchestrator.execute.side_effect = RuntimeError(
        "detalhe interno sensível"
    )

    client = create_test_client(
        document_parser,
        orchestrator,
    )

    response = client.post(
        "/api/v1/assessments",
        data={
            "job_description": (
                "Descrição válida da vaga"
            ),
        },
        files={
            "resume": (
                "resume.pdf",
                b"conteudo-do-pdf",
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": (
            "Não foi possível processar "
            "o assessment."
        )
    }

    assert (
        "detalhe interno sensível"
        not in response.text
    )