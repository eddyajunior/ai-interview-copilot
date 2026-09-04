from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.schemas.candidate_assessment import CandidateAssessment
from app.services.assessment_orchestrator import AssessmentOrchestrator
from app.services.document_parser import (
    DocumentParser,
    UnsupportedDocumentTypeError,
)


router = APIRouter(
    prefix="/api/v1/assessments",
    tags=["assessments"],
)


ALLOWED_RESUME_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
}


def get_document_parser() -> DocumentParser:
    return DocumentParser()


def get_assessment_orchestrator() -> AssessmentOrchestrator:
    return AssessmentOrchestrator()


@router.post(
    "",
    response_model=CandidateAssessment,
    status_code=status.HTTP_200_OK,
)
async def create_assessment(
    job_description: str = Form(...),
    resume: UploadFile = File(...),
    document_parser: DocumentParser = Depends(
        get_document_parser
    ),
    orchestrator: AssessmentOrchestrator = Depends(
        get_assessment_orchestrator
    ),
) -> CandidateAssessment:
    if not job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A descrição da vaga não pode estar vazia.",
        )

    if not resume.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O currículo deve possuir um nome de arquivo.",
        )

    extension = Path(resume.filename).suffix.lower()

    if extension not in ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Formato de currículo não suportado. "
                "Utilize TXT, PDF ou DOCX."
            ),
        )

    resume_content = await resume.read()

    if not resume_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O arquivo do currículo não pode estar vazio.",
        )

    temporary_path: Path | None = None

    try:
        job_document = document_parser.parse_text(
            job_description,
            source_name="job_description",
        )

        with NamedTemporaryFile(
            mode="wb",
            suffix=extension,
            delete=False,
        ) as temporary_file:
            temporary_file.write(resume_content)

            temporary_path = Path(
                temporary_file.name
            )

        resume_document = document_parser.parse(
            temporary_path
        )

        return orchestrator.execute(
            job_document,
            resume_document,
        )

    except UnsupportedDocumentTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Não foi possível processar "
                "o assessment."
            ),
        ) from exc

    finally:
        if (
            temporary_path is not None
            and temporary_path.exists()
        ):
            temporary_path.unlink()